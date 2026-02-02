# Subdatasets Report

**Source File:** `data/customer_support_tickets.csv`
**Total Tickets:** 8,469
**Total Subdatasets:** 53

## Generated Subdatasets

### Random Sample

- **random_sample_50.csv** (50 tickets)
  - Random sample of 50 tickets
- **random_sample_100.csv** (100 tickets)
  - Random sample of 100 tickets
- **random_sample_200.csv** (200 tickets)
  - Random sample of 200 tickets
- **random_sample_500.csv** (500 tickets)
  - Random sample of 500 tickets
- **random_sample_1000.csv** (1,000 tickets)
  - Random sample of 1000 tickets
- **random_sample_2000.csv** (2,000 tickets)
  - Random sample of 2000 tickets

### Filter By Ticket Type

- **ticket_type_refund_request.csv** (1,752 tickets)
  - All tickets of type: Refund request
- **ticket_type_technical_issue.csv** (1,747 tickets)
  - All tickets of type: Technical issue
- **ticket_type_cancellation_request.csv** (1,695 tickets)
  - All tickets of type: Cancellation request
- **ticket_type_product_inquiry.csv** (1,641 tickets)
  - All tickets of type: Product inquiry
- **ticket_type_billing_inquiry.csv** (1,634 tickets)
  - All tickets of type: Billing inquiry

### Filter By Priority

- **priority_medium.csv** (2,192 tickets)
  - All Medium priority tickets
- **priority_critical.csv** (2,129 tickets)
  - All Critical priority tickets
- **priority_high.csv** (2,085 tickets)
  - All High priority tickets
- **priority_low.csv** (2,063 tickets)
  - All Low priority tickets

### Filter By Status

- **status_pending_customer_response.csv** (2,881 tickets)
  - All tickets with status: Pending Customer Response
- **status_open.csv** (2,819 tickets)
  - All tickets with status: Open
- **status_closed.csv** (2,769 tickets)
  - All tickets with status: Closed

### Filter By Product

- **product_canon_eos.csv** (240 tickets)
  - All tickets for product: Canon EOS
- **product_gopro_hero.csv** (228 tickets)
  - All tickets for product: GoPro Hero
- **product_nest_thermostat.csv** (225 tickets)
  - All tickets for product: Nest Thermostat
- **product_philips_hue_lights.csv** (221 tickets)
  - All tickets for product: Philips Hue Lights
- **product_amazon_echo.csv** (221 tickets)
  - All tickets for product: Amazon Echo
- **product_lg_smart_tv.csv** (219 tickets)
  - All tickets for product: LG Smart TV
- **product_sony_xperia.csv** (217 tickets)
  - All tickets for product: Sony Xperia
- **product_roomba_robot_vacuum.csv** (216 tickets)
  - All tickets for product: Roomba Robot Vacuum
- **product_apple_airpods.csv** (213 tickets)
  - All tickets for product: Apple AirPods
- **product_lg_oled.csv** (213 tickets)
  - All tickets for product: LG OLED

### Filter By Channel

- **channel_email.csv** (2,143 tickets)
  - All tickets from Email channel
- **channel_phone.csv** (2,132 tickets)
  - All tickets from Phone channel
- **channel_social_media.csv** (2,121 tickets)
  - All tickets from Social media channel
- **channel_chat.csv** (2,073 tickets)
  - All tickets from Chat channel

### Stratified Sample

- **stratified_sample_50.csv** (50 tickets)
  - Stratified sample of 50 tickets (balanced by ticket type)
- **stratified_sample_100.csv** (100 tickets)
  - Stratified sample of 100 tickets (balanced by ticket type)
- **stratified_sample_200.csv** (200 tickets)
  - Stratified sample of 200 tickets (balanced by ticket type)
- **stratified_sample_500.csv** (500 tickets)
  - Stratified sample of 500 tickets (balanced by ticket type)
- **stratified_sample_1000.csv** (1,000 tickets)
  - Stratified sample of 1000 tickets (balanced by ticket type)
- **stratified_sample_2000.csv** (2,000 tickets)
  - Stratified sample of 2000 tickets (balanced by ticket type)

### Edge Case

- **edge_case_missing_ratings.csv** (100 tickets)
  - Tickets without satisfaction ratings

### Filter By Quality

- **quality_high_satisfaction.csv** (500 tickets)
  - Tickets with high satisfaction ratings (4-5 stars)
- **quality_low_satisfaction.csv** (500 tickets)
  - Tickets with low satisfaction ratings (1-2 stars)

### Filter By Date

- **time_recent_2021_onwards.csv** (1,000 tickets)
  - Recent tickets (2021 onwards)
- **time_older_before_2021.csv** (1,000 tickets)
  - Older tickets (before 2021)

### Excel Export

- **excel/random_sample_100.xlsx** (100 tickets)
  - Random sample - 100 tickets (Excel format)
- **excel/random_sample_500.xlsx** (500 tickets)
  - Random sample - 500 tickets (Excel format)
- **excel/stratified_sample_100.xlsx** (100 tickets)
  - Stratified sample - 100 tickets (Excel format)
- **excel/ticket_type_technical_issue.xlsx** (1,747 tickets)
  - Technical issues only (Excel format)
- **excel/ticket_type_billing_inquiry.xlsx** (1,634 tickets)
  - Billing inquiries only (Excel format)
- **excel/priority_critical.xlsx** (2,129 tickets)
  - Critical priority tickets (Excel format)
- **excel/status_open.xlsx** (2,819 tickets)
  - Open tickets (Excel format)
- **excel/quality_high_satisfaction.xlsx** (500 tickets)
  - High satisfaction ratings (Excel format)
- **excel/quality_low_satisfaction.xlsx** (500 tickets)
  - Low satisfaction ratings (Excel format)
- **excel/channel_email.xlsx** (2,143 tickets)
  - Email channel tickets (Excel format)

## Usage

```bash
# Upload any subdataset to the Semantic Classifier
streamlit run app.py
```

## Dataset Statistics

- **Ticket Types:** 5
- **Products:** 42
- **Priorities:** 4
- **Channels:** 4
- **Statuses:** 3
