{% extends 'django_openstack/syspanel/base.html' %}
{% load sizeformat %}

{# default landing page for a admin user #}
{# nav bar on top, sidebar, overview info in main #}

{% block sidebar %}
  {% with current_sidebar="bills" %}
    {{block.super}}
  {% endwith %}
{% endblock %}

{% block page_header %}
  {# to make searchable false, just remove it from the include statement #}
  {% include "django_openstack/common/_page_header.html" with title="BILLING" %}
{% endblock page_header %}

{% block syspanel_main %}
  <div id="status_top">
        {% if external_links %}
          <div id="monitoring">
            <h3>Monitoring: </h3>
            <ul id="external_links">
              {% for link in external_links %}
                <li><a target="_blank" href="{{ link.1 }}">{{ link.0 }}</a></li>
              {% endfor %}
            </ul>
          </div>
        {% endif %}

        <form action="" method="get" id="date_form">
          <!-- {% csrf_token %} -->
          <h3> Select a month to query its usage: </h3>
          <div class="form-row">
            {{ dateform.date }}
            <input class="submit" type="submit"/>
          </div>
        </form>

        <ul class='status_box good'>


          <li class='block'>
            <p class='overview'><span class='used'> VCPU :</span> ${{global_cost.vcpus|floatformat}}</p>
            <p class='used'>{{global_summary.total_vcpus}}<span class='label'> Cores</span></p>   
            <p class='used'>{{global_summary.total_active_vcpus}}<span class='label'> Used</span></p>
            <p class='avail'>{{global_summary.total_avail_vcpus}}<span class='label'> Avail</span></p>
          </li>
          <li class='block'>
            <p class='overview'><span class='used'> RAM :</span> ${{global_cost.ram|floatformat}}</p>
            <p class='used'>{{global_summary.total_ram_size_hr|floatformat}}<span class='unit'> {{global_summary.unit_ram_size}}</span><span class='label'> Total</span></p>
            <p class='used'>{{global_summary.total_active_ram_size_hr|floatformat}}<span class='unit'> {{global_summary.unit_ram_size}}</span><span class='label'> Used</span></p>
            <p class='avail'>{{global_summary.total_avail_ram_size_hr|floatformat}}<span class='unit'> {{global_summary.unit_ram_size}}</span><span class='label'> Avail</span></p>
          </li>
         <li class='block last'>
            <p class='overview'><span class='used'> VDISK :</span> ${{global_cost.vdisk|floatformat}}</p>
            <p class='used'>{{global_summary.total_disk_size_hr|floatformat}}<span class='unit'> {{global_summary.unit_disk_size}}</span><span class='label'> Total</span></p>
            <p class='used'>{{global_summary.total_active_disk_size_hr|floatformat}}<span class='unit'> {{global_summary.unit_disk_size}}</span><span class='label'> Used</span></p>
            <p class='avail'>{{global_summary.total_avail_disk_size_hr|floatformat}}<span class='unit'> {{global_summary.unit_disk_size}}</span><span class='label'> Avail</span></p>
          </li>
          <li class='block'>
          </li>

          </li>
      </li>

          </li>
        </ul>

        <p id="activity">
          <span><strong>Active Instances:</strong> {{global_summary.total_active_instances|default:'-'}}</span>
          <span><strong>This month's VCPU-Hours:</strong> {{global_summary.total_cpu_usage|floatformat|default:'-'}}</span>
          <span><strong>This month's GB-Hours:</strong> {{global_summary.total_disk_usage|floatformat|default:'-'}}</span>
        </p>
    
  </div>
  <br>
  <h2>Unit Cost </h2>
  <div id="Unit_cost">
      {% include "django_openstack/syspanel/bills/_unit_cost.html" %}
  </div>

  {% if usage_list %}
  <div id="usage_table">
    <div class='table_title wide'>
      <a class="csv_download_link" href="{{csv_link}}">Download CSV &raquo;</a>
      <h3>Server Usage Summary</h3>
    </div>

    <table class="wide">
      <tr id="headings">
        <th>Tenant</th>
        <th>Instances</th>
        <th>VCPUs</th>
        <th>Disk</th>
        <th>RAM</th>
        <th>VCPU CPU-Hours</th>
        <th>Disk GB-Hours</th>
      </tr>
      {% for usage in usage_list %}
        <tr>
          <td><a href="{% url syspanel_tenant_usage usage.tenant_id %}">{{usage.tenant_id}}</a></td>
          <td>{{usage.total_active_instances}}</td>
          <td>{{usage.total_active_vcpus}}</td>
          <td>{{usage.total_active_disk_size|diskgbformat}}</td>
          <td>{{usage.total_active_ram_size|mbformat}}</td>
          <td>{{usage.total_cpu_usage|floatformat}}</td>
          <td>{{usage.total_disk_usage|floatformat}}</td>
        </tr>
      {% endfor %}
  </div>
    {% endif %}

 </div>
  
</div>

{% endblock %}
