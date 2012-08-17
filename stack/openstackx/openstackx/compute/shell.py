"""
Command-line interface to the OpenStack Compute API.
"""

import argparse
import getpass
import httplib2
import os
import prettytable
import sys
from openstack import compute

# Choices for flags.
DAY_CHOICES = [getattr(compute, i).lower()
               for i in dir(compute)
               if i.startswith('BACKUP_WEEKLY_')]
HOUR_CHOICES = [getattr(compute, i).lower()
                for i in dir(compute)
                if i.startswith('BACKUP_DAILY_')]

def pretty_choice_list(l): return ', '.join("'%s'" % i for i in l)

# Sentinal for boot --key
AUTO_KEY = object()

# Decorator for args
def arg(*args, **kwargs):
    def _decorator(func):
        # Because of the sematics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        func.__dict__.setdefault('arguments', []).insert(0, (args, kwargs))
        return func
    return _decorator

class CommandError(Exception):
    pass

def env(e):
    return os.environ.get(e, '')

class ComputeShell(object):

    # Hook for the test suite to inject a fake server.
    _api_class = compute.Compute

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog = 'openstack-compute',
            description = __doc__.strip(),
            epilog = 'See "openstack-compute help COMMAND" for help on a specific command.',
            add_help = False,
            formatter_class = ComputeHelpFormatter,
        )

        # Global arguments
        self.parser.add_argument('-h', '--help',
            action = 'help',
            help = argparse.SUPPRESS,
        )

        self.parser.add_argument('--debug',
            default = False,
            action = 'store_true',
            help = argparse.SUPPRESS)

        self.parser.add_argument('-f', '--config-file',
            metavar = 'PATH',
            default = None,
            help = 'Path to config file (default: ~/.openstack/compute.conf)')
        self.parser.add_argument('--username',
            help = 'Account username. Required if not in a config file/environ.')
        self.parser.add_argument('--apikey',
            help = 'Account API key. Required if not in a config file/environ.')
        self.parser.add_argument('--auth-url',
            help = "Service URL (default: Rackspace's US auth URL)")
        self.parser.add_argument('--allow-cache',
            action = 'store_true',
            default = False,
            help = "Allow the API to returned cached results.")
        self.parser.add_argument('--cloud-api',
            help = "API of the cloud service to be managed: either RACKSPACE or OPENSTACK")

        # Subcommands
        subparsers = self.parser.add_subparsers(metavar='<subcommand>')
        self.subcommands = {}

        # Everything that's do_* is a subcommand.
        for attr in (a for a in dir(self) if a.startswith('do_')):
            # I prefer to be hypen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            callback = getattr(self, attr)
            desc = callback.__doc__ or ''
            help = desc.strip().split('\n')[0]
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(command,
                help = help,
                description = desc,
                add_help=False,
                formatter_class = ComputeHelpFormatter
            )
            subparser.add_argument('-h', '--help',
                action = 'help',
                help = argparse.SUPPRESS,
            )
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def main(self, argv):
        # Parse args and call whatever callback was selected
        args = self.parser.parse_args(argv)

        # Short-circuit and deal with help right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0

        # Deal with global arguments
        if args.debug:
            httplib2.debuglevel = 1

        self.compute = self._api_class(
            config_file = args.config_file,
            username = args.username,
            apikey = args.apikey,
            auth_url = args.auth_url,
            allow_cache = args.allow_cache,
        )
        if not self.compute.config.username:
            raise CommandError("You must provide a username, either via "
                               "--username or env[OPENSTACK_COMPUTE_USERNAME], "
                               "or a config file.")
        if not self.compute.config.apikey:
            raise CommandError("You must provide an API key, either via "
                               "--apikey or via env[OPENSTACK_COMPUTE_APIKEY], "
                               "or a config file.")
        try:
            self.compute.authenticate()
        except compute.Unauthorized:
            raise CommandError("Invalid Cloud Servers credentials.")

        args.func(args)

    @arg('command', metavar='<subcommand>', nargs='?', help='Display help for <subcommand>')
    def do_help(self, args):
        """
        Display help about this program or one of its subcommands.
        """
        if args.command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise CommandError("'%s' is not a valid subcommand." % args.command)
        else:
            self.parser.print_help()

    @arg('server', metavar='<server>', help='Name or ID of server.')
    @arg('--enable', dest='enabled', default=None, action='store_true', help='Enable backups.')
    @arg('--disable', dest='enabled', action='store_false', help='Disable backups.')
    @arg('--weekly', metavar='<day>', choices=DAY_CHOICES,
         help='Schedule a weekly backup for <day> (one of: %s).' % pretty_choice_list(DAY_CHOICES))
    @arg('--daily', metavar='<time-window>', choices=HOUR_CHOICES,
         help='Schedule a daily backup during <time-window> (one of: %s).' % pretty_choice_list(HOUR_CHOICES))
    def do_backup_schedule(self, args):
        """
        Show or edit the backup schedule for a server.

        With no flags, the backup schedule will be shown. If flags are given,
        the backup schedule will be modified accordingly.
        """
        server = self._find_server(args.server)

        # If we have some flags, update the backup
        backup = {}
        if args.daily:
            backup['daily'] = getattr(compute, 'BACKUP_DAILY_%s' % args.daily.upper())
        if args.weekly:
            backup['weekly'] = getattr(compute, 'BACKUP_WEEKLY_%s' % args.weekly.upper())
        if args.enabled is not None:
            backup['enabled'] = args.enabled
        if backup:
            server.backup_schedule.update(**backup)
        else:
            print_dict(server.backup_schedule._info)

    @arg('server', metavar='<server>', help='Name or ID of server.')
    def do_backup_schedule_delete(self, args):
        """
        Delete the backup schedule for a server.
        """
        server = self._find_server(args.server)
        server.backup_schedule.delete()

    @arg('--flavor',
         default = None,
         metavar = '<flavor>',
         help = "Flavor ID (see 'cloudservers flavors'). Defaults to 256MB RAM instance.")
    @arg('--image',
         default = None,
         metavar = '<image>',
         help = "Image ID (see 'cloudservers images'). Defaults to Ubuntu 10.04 LTS.")
    @arg('--ipgroup',
         default = None,
         metavar = '<group>',
         help = "IP group name or ID (see 'cloudservers ipgroup-list'). DEPRICATED in OpenStack")
    @arg('--meta',
         metavar = "<key=value>",
         action = 'append',
         default = [],
         help = "Record arbitrary key/value metadata. May be give multiple times.")
    @arg('--file',
         metavar = "<dst-path=src-path>",
         action = 'append',
         dest = 'files',
         default = [],
         help = "Store arbitrary files from <src-path> locally to <dst-path> "\
                "on the new server. You may store up to 5 files.")
    @arg('--key',
         metavar = '<path>',
         nargs = '?',
         const = AUTO_KEY,
         help = "Key the server with an SSH keypair. Looks in ~/.ssh for a key, "\
                "or takes an explicit <path> to one.")
    @arg('name', metavar='<name>', help='Name for the new server')
    def do_boot(self, args):
        """Boot a new server."""
        flavor = args.flavor or self.compute.flavors.find(ram=256)
        image = args.image or self.compute.images.find(name="Ubuntu 10.04 LTS (lucid)")

        # Map --ipgroup <name> to an ID.
        # XXX do this for flavor/image?
        if args.ipgroup:
            ipgroup = self._find_ipgroup(args.ipgroup)
        else:
            ipgroup = None

        metadata = dict(v.split('=') for v in args.meta)

        files = {}
        for f in args.files:
            dst, src = f.split('=', 1)
            try:
                files[dst] = open(src)
            except IOError, e:
                raise CommandError("Can't open '%s': %s" % (src, e))

        if args.key is AUTO_KEY:
            possible_keys = [os.path.join(os.path.expanduser('~'), '.ssh', k)
                             for k in ('id_dsa.pub', 'id_rsa.pub')]
            for k in possible_keys:
                if os.path.exists(k):
                    keyfile = k
                    break
            else:
                raise CommandError("Couldn't find a key file: tried ~/.ssh/id_dsa.pub or ~/.ssh/id_rsa.pub")
        elif args.key:
            keyfile = args.key
        else:
            keyfile = None

        if keyfile:
            try:
                files['/root/.ssh/authorized_keys2'] = open(keyfile)
            except IOError, e:
                raise CommandError("Can't open '%s': %s" % (keyfile, e))

        server = self.compute.servers.create(args.name, image, flavor, ipgroup, metadata, files)
        print_dict(server._info)

    def do_flavor_list(self, args):
        """Print a list of available 'flavors' (sizes of servers)."""
        print_list(self.compute.flavors.list(), ['ID', 'Name', 'RAM', 'Disk'])

    def do_image_list(self, args):
        """Print a list of available images to boot from."""
        print_list(self.compute.images.list(), ['ID', 'Name', 'Status'])

    @arg('server', metavar='<server>', help='Name or ID of server.')
    @arg('name', metavar='<name>', help='Name for the new image.')
    def do_image_create(self, args):
        """Create a new image by taking a snapshot of a running server."""
        server = self._find_server(args.server)
        image = self.compute.images.create(args.name, server)
        print_dict(image._info)

    @arg('image', metavar='<image>', help='Name or ID of image.')
    def do_image_delete(self, args):
        """
        Delete an image.

        It should go without saying, but you cn only delete images you
        created.
        """
        image = self._find_image(args.image)
        image.delete()

    @arg('server', metavar='<server>', help='Name or ID of server.')
    @arg('group', metavar='<group>', help='Name or ID of group.')
    @arg('address', metavar='<address>', help='IP address to share.')
    def do_ip_share(self, args):
        """Share an IP address from the given IP group onto a server."""
        server = self._find_server(args.server)
        group = self._find_ipgroup(args.group)
        server.share_ip(group, args.address)

    @arg('server', metavar='<server>', help='Name or ID of server.')
    @arg('address', metavar='<address>', help='Shared IP address to remove from the server.')
    def do_ip_unshare(self, args):
        """Stop sharing an given address with a server."""
        server = self._find_server(args.server)
        server.unshare_ip(args.address)

    def do_ipgroup_list(self, args):
        """Show IP groups."""
        def pretty_server_list(ipgroup):
            return ", ".join(self.compute.servers.get(id).name for id in ipgroup.servers)

        print_list(self.compute.ipgroups.list(),
                   fields = ['ID', 'Name', 'Server List'],
                   formatters = {'Server List': pretty_server_list})

    @arg('group', metavar='<group>', help='Name or ID of group.')
    def do_ipgroup_show(self, args):
        """Show details about a particular IP group."""
        group = self._find_ipgroup(args.group)
        print_dict(group._info)

    @arg('name', metavar='<name>', help='What to name this new group.')
    @arg('server', metavar='<server>', nargs='?',
         help='Server (name or ID) to make a member of this new group.')
    def do_ipgroup_create(self, args):
        """Create a new IP group."""
        if args.server:
            server = self._find_server(args.server)
        else:
            server = None
        group = self.compute.ipgroups.create(args.name, server)
        print_dict(group._info)

    @arg('group', metavar='<group>', help='Name or ID of group.')
    def do_ipgroup_delete(self, args):
        """Delete an IP group."""
        self._find_ipgroup(args.group).delete()

    def do_list(self, args):
        """List active servers."""
        print_list(self.compute.servers.list(), ['ID', 'Name', 'Status', 'Public IP', 'Private IP'])

    @arg('--hard',
        dest = 'reboot_type',
        action = 'store_const',
        const = compute.REBOOT_HARD,
        default = compute.REBOOT_SOFT,
        help = 'Perform a hard reboot (instead of a soft one).')
    @arg('server', metavar='<server>', help='Name or ID of server.')
    def do_reboot(self, args):
        """Reboot a server."""
        self._find_server(args.server).reboot(args.reboot_type)

    @arg('server', metavar='<server>', help='Name or ID of server.')
    @arg('image', metavar='<image>', help="Name or ID of new image.")
    def do_rebuild(self, args):
        """Shutdown, re-image, and re-boot a server."""
        server = self._find_server(args.server)
        image = self._find_image(args.image)
        server.rebuild(image)

    @arg('server', metavar='<server>', help='Name (old name) or ID of server.')
    @arg('name', metavar='<name>', help='New name for the server.')
    def do_rename(self, args):
        """Rename a server."""
        self._find_server(args.server).update(name=args.name)

    @arg('server', metavar='<server>', help='Name or ID of server.')
    @arg('flavor', metavar='<flavor>', help = "Name or ID of new flavor.")
    def do_resize(self, args):
        """Resize a server."""
        server = self._find_server(args.server)
        flavor = self._find_flavor(args.flavor)
        server.resize(flavor)

    @arg('server', metavar='<server>', help='Name or ID of server.')
    def do_resize_confirm(self, args):
        """Confirm a previous resize."""
        self._find_server(args.server).confirm_resize()

    @arg('server', metavar='<server>', help='Name or ID of server.')
    def do_resize_revert(self, args):
        """Revert a previous resize (and return to the previous VM)."""
        self._find_server(args.server).revert_resize()

    @arg('server', metavar='<server>', help='Name or ID of server.')
    def do_root_password(self, args):
        """
        Change the root password for a server.
        """
        server = self._find_server(args.server)
        p1 = getpass.getpass('New password: ')
        p2 = getpass.getpass('Again: ')
        if p1 != p2:
            raise CommandError("Passwords do not match.")
        server.update(password=p1)

    @arg('server', metavar='<server>', help='Name or ID of server.')
    def do_show(self, args):
        """Show details about the given server."""
        s = self.compute.servers.get(self._find_server(args.server))

        info = s._info.copy()
        addresses = info.pop('addresses')
        for addrtype in addresses:
            info['%s ip' % addrtype] = ', '.join(addresses[addrtype])

        info['flavor'] = self._find_flavor(info.pop('flavorId')).name
        info['image'] = self._find_image(info.pop('imageId')).name

        print_dict(info)

    @arg('server', metavar='<server>', help='Name or ID of server.')
    def do_delete(self, args):
        """Immediately shut down and delete a server."""
        self._find_server(args.server).delete()

    def _find_server(self, server):
        """Get a server by name or ID."""
        return self._find_resource(self.compute.servers, server)

    def _find_ipgroup(self, group):
        """Get an IP group by name or ID."""
        return self._find_resource(self.compute.ipgroups, group)
    
    def _find_image(self, image):
        """Get an image by name or ID."""
        return self._find_resource(self.compute.images, image)

    def _find_flavor(self, flavor):
        """Get a flavor by name, ID, or RAM size."""
        try:
            return self._find_resource(self.compute.flavors, flavor)
        except compute.NotFound:
            return self.compute.flavors.find(ram=flavor)

    def _find_resource(self, manager, name_or_id):
        """Helper for the _find_* methods."""
        try:
            if isinstance(name_or_id, int) or name_or_id.isdigit():
                return manager.get(int(name_or_id))
            else:
                return manager.find(name=name_or_id)
        except compute.NotFound:
            raise CommandError("No %s with a name or ID of '%s' exists."
                               % (manager.resource_class.__name__.lower(), name_or_id))

# I'm picky about my shell help.
class ComputeHelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(ComputeHelpFormatter, self).start_section(heading)

# Helpers
def print_list(objs, fields, formatters={}):
    pt = prettytable.PrettyTable([f for f in fields], caching=False)
    pt.aligns = ['l' for f in fields]

    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                row.append(getattr(o, field.lower().replace(' ', '_'), ''))
        pt.add_row(row)

    pt.printt(sortby=fields[0])

def print_dict(d):
    pt = prettytable.PrettyTable(['Property', 'Value'], caching=False)
    pt.aligns = ['l', 'l']
    [pt.add_row(list(r)) for r in d.iteritems()]
    pt.printt(sortby='Property')

def main():
    try:
        ComputeShell().main(sys.argv[1:])
    except CommandError, e:
        print >> sys.stderr, e
        sys.exit(1)