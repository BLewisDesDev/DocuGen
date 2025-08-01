# CAURA CHSP CARE PLAN

## CLIENT DETAILS

**Name:** {{ FirstName }} {{ LastName }}
**Gender:** {{ Gender }}
**D.O.B:** {{ DOB }}
**Marital stat:** {{ MaritalStatus }}
**Phone:** {{Phone }}
**Address:** {{ Address1 }} {{ Address2 }} {{ Suburb }} NSW, {{ PostCode }}

## CONDITIONS AND HISTORY

{{ Concerns }}

## EMERGENCY OR NEXT OF KIN CONTACT DETAILS

**Name:** {{ KinFirstName }} {{ KinLastName }}
**Relationship:** {{ KinRelationship  }}
**Phone:** {{ KinPhone }}
**Address:** {{ KinAddress }}

## SERVICES

**Home Maintenance:**
{% if Type == "HM" %}☑ Yes ☐ No {% else % }☐ Yes  ☑ No {% endif %}
**Domestic Assistance:**
{% if Type == "DA" %}☑ Yes ☐ No {% else %}☐ Yes ☑ No {% endif %}
**CLIENT GOALS**
{% if Goal1%}1. {{ Goal1 }} {% else %} N/A {% endif %}
{% if Goal1%}2. {{ Goal2 }} {% endif %}
{% if Goal1%}3. {{ Goal3 }} {% endif %}

## SERVICE DETAILS

**CARE NEEDS GOAL INTERVENTION**
{{ CareNeed1 }} {{ Goal1 }} {{ Intervention1 }}
{{ CareNeed2 }} {{ Goal2 }} {{ Intervention2 }}
{{ CareNeed3  }} {{ Goal3 }} {{ Intervention3 }}

## WHS ISSUES/ FIRE SAFETY AND EMERGENCY EVACUATION PLAN

{% if FSEP == “true” %} Fire Saftey Plan Created : ☑ Yes ☐ No {% else %} ☐ Yes ☑ No {% endif %}
WHS Issues:
{% if WHSIssues%}1. {{ WHSIssues }} {% else %} N/A {% endif %}

## EMERGENCY RESPONSE PLAN

{% if EP == “true” %}☑ Yes ☐ No {% else %}☐ Yes ☑ No {% endif %}

## OTHER INFO

{% if OtherInfo%} {{ OtherInfo }} {% else %} N/A {% endif %}

## ASSISTANCE TASKS

**ASSISTANCE TASKS**
{{ Task1 }}
{{ Task2 }}
{{ Task3 }}
{{ Task4 }}

## LAST UPDATED

**Date:** {{ UpdateDate }}
**Signed:**
**Name:** {{ StaffName }}
**Date:** {{ StaffSignedDate }}
