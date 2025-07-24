# CAURA CHSP CARE PLAN

## CLIENT DETAILS

**Name:** {{ FirstName }} {{ LastName }}
**Gender:** {{ Gender }}
**D.O.B:** {{ DOB }}
**Marital Status:** {{ MaritalStatus }}
**Phone:** {{ Phone }}
**Address:** {{ Address1 }} {{ Address2 }} {{ Suburb }} NSW, {{ PostCode }}

## CONDITIONS AND HISTORY

{{ Concerns }}

## EMERGENCY OR NEXT OF KIN CONTACT DETAILS

**Name:** {{ KinFirstName }} {{ KinLastName }}
**Relationship:** {{ KinRelationship }}
**Phone:** {{ KinPhone }}
**Address:** {{ KinAddress }}

## CHSP SERVICES APPROVED

**Garden Maintenance:**
{% if Type == "HM" or "HM" in ServiceTypes %}☑ Yes ☐ No{% else %}☐ Yes ☑ No{% endif %}

**Domestic Assistance:**
{% if Type == "DA" or "DA" in ServiceTypes %}☑ Yes ☐ No{% else %}☐ Yes ☑ No{% endif %}

## SERVICE SCHEDULE

**Garden Maintenance:** {% if Type == "HM" or "HM" in ServiceTypes %}Monthly visits{% else %}Not applicable{% endif %}
**Property Riskmitigation Services:** {% if Type == "HM" or "HM" in ServiceTypes %}2 comprehensive services per year{% else %}Not applicable{% endif %}
**Domestic Assistance:** {% if Type == "DA" or "DA" in ServiceTypes %}Fortnightly 2-hour sessions{% else %}Not applicable{% endif %}

**SERVICE COMMENCEMENT:** {{ ServiceStartDate }}
**PLAN REVIEW DATE:** {{ NextReviewDate }}

## CLIENT GOALS (Wellness & Reablement Focused)

{% if Goal1 %}1. {{ Goal1 }}{% else %}N/A{% endif %}
{% if Goal2 %}2. {{ Goal2 }}{% else %}{% endif %}
{% if Goal3 %}3. {{ Goal3 }}{% else %}{% endif %}

## SERVICE DETAILS TABLE

| **CARE NEED**   | **GOAL**    | **INTERVENTION**    | **FREQUENCY**    |
| --------------- | ----------- | ------------------- | ---------------- |
| {{ CareNeed1 }} | {{ Goal1 }} | {{ Intervention1 }} | {{ Frequency1 }} |
| {{ CareNeed2 }} | {{ Goal2 }} | {{ Intervention2 }} | {{ Frequency2 }} |
| {{ CareNeed3 }} | {{ Goal3 }} | {{ Intervention3 }} | {{ Frequency3 }} |

## WELLNESS AND REABLEMENT APPROACH

**Approach Used:** {% if WellnessApproach %}{{ WellnessApproach }}{% else %}Standard wellness approach focusing on maintaining independence{% endif %}
Time-Limited Services: {% if TimeLimitedServices == "true" %}☑ Yes ☐ No{% else %}☐ Yes ☑ No{% endif %}
Review Period: {{ ReviewPeriod | default("12 months") }}

## WORK HEALTH AND SAFETY ASSESSMENT

**WHS Assessment Completed:** {% if WHSAssessmentComplete == "true" %}☑ Yes ☐ No{% else %}☐ Yes ☑ No{% endif %}
Assessment Date: {{ WHSAssessmentDate }}

**IDENTIFIED WHS RISKS:**
{% if WHSIssues %}{{ WHSIssues }}{% else %}No specific risks identified at time of assessment{% endif %}

**RISK MITIGATION MEASURES:**
{% if RiskMitigation %}{{ RiskMitigation }}{% else %}Standard safety protocols to be followed{% endif %}

**FIRE SAFETY AND EMERGENCY EVACUATION PLAN**
Fire Safety Plan Required: {% if FSEP == "true" %}☑ Yes ☐ No{% else %}☐ Yes ☑ No{% endif %}
Plan Completed: {% if FSPCompleted == "true" %}☑ Yes ☐ No{% else %}☐ Yes ☑ No{% endif %}

**EMERGENCY RESPONSE PLAN**
Emergency Plan Required: {% if EP == "true" %}☑ Yes ☐ No{% else %}☐ Yes ☑ No{% endif %}
Plan Details: {% if EmergencyPlanDetails %}{{ EmergencyPlanDetails }}{% else %}Standard emergency procedures apply{% endif %}

**ASSISTANCE TASKS (CAURA SERVICES)**
{% if Task1 %}• {{ Task1 }}{% endif %}
{% if Task2 %}• {{ Task2 }}{% endif %}
{% if Task3 %}• {{ Task3 }}{% endif %}
{% if Task4 %}• {{ Task4 }}{% endif %}

## CAURA SERVICE MODEL

Garden Maintenance Focus: Monthly visits for essential pruning, yard clearance, and lawn mowing to maintain client safety and property access
Make-Safe Services: Biannual comprehensive property assessments including window cleaning, gutter cleaning, hazard identification and safety repairs
Domestic Assistance Focus: Fortnightly 2-hour house cleaning sessions with occasional unaccompanied shopping support as required

### CLIENT CONTRIBUTION ARRANGEMENTS

Fee Structure: {{ ClientContribution | default("As per Caura's Client Contribution Policy") }}
Hardship Provisions Explained: {% if HardshipExplained == "true" %}☑ Yes ☐ No{% else %}☐ Yes ☑ No{% endif %}

### SERVICE MONITORING AND REVIEW

12-Month Review Due: {{ TwelveMonthReviewDate }}
Support Plan Reviews: As required based on changing needs
My Aged Care Record Updated: {% if MACRecordUpdated == "true" %}☑ Yes ☐ No{% else %}☐ Yes ☑ No{% endif %}

### ADDITIONAL INFORMATION

Cultural/Linguistic Needs: {% if CulturalNeeds %}{{ CulturalNeeds }}{% else %}None identified{% endif %}
Accessibility Requirements: {% if AccessibilityNeeds %}{{ AccessibilityNeeds }}{% else %}None identified{% endif %}
Other Information: {% if OtherInfo %}{{ OtherInfo }}{% else %}N/A{% endif %}

### AGED CARE QUALITY STANDARDS COMPLIANCE

This care plan has been developed in accordance with the Aged Care Quality Standards and CHSP Program Manual requirements.

## PLAN APPROVAL AND SIGNATURES

**Care Plan Created By:** {{ StaffName }}
**Position:** {{ StaffPosition | default("Care Coordinator") }}
**Date:** {{ PlanCreatedDate }}
**Signature:**

**Client Consultation Completed:** {% if ClientConsulted == "true" %}☑ Yes ☐ No{% else %}☐ Yes ☑ No{% endif %}
**Client Name:** {{ FirstName }} {{ LastName }}
**Date:** {{ ClientConsultDate }}
**Client/Representative Signature:**

### Supervisor Review

**Reviewed By:** {{ SupervisorName }}
**Date:** {{ SupervisorReviewDate }}
**Signature:**

### LAST UPDATED

**Date:** {{ UpdateDate }}
**Updated By:** {{ UpdatedBy }}
**Reason for Update:** {{ UpdateReason | default("Routine review") }}
