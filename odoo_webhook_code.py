'''
Paste this code into the Odoo Webhook 
'''

# Configuration
FORGOT_THRESHOLD = 14 
DOUBLE_TAP_GAP = 30
now = datetime.datetime.now()

# 1. Get the Card ID from the Pi
card_id = payload.get('card_id')

if card_id:
    # 2. Find the employee who has this card ID in their 'Barcode' field
    employee = env['hr.employee'].search([('barcode', '=', card_id)], limit=1)
    
    if not employee:
        # This will show up in Odoo's logs if a stranger taps a card
        log("No employee found with Barcode: %s" % card_id, level='error')
    else:
        # 3. Find their last attendance record
        last_attendance = env['hr.attendance'].search([
            ('employee_id', '=', employee.id)
        ], limit=1, order='check_in desc')

        # 4. Double-Tap Protection
        skip_tap = False
        if last_attendance:
            last_event = last_attendance.check_out or last_attendance.check_in
            if (now - last_event).total_seconds() < DOUBLE_TAP_GAP:
                skip_tap = True

        if not skip_tap:
            # SCENARIO: Currently Checked In
            if last_attendance and not last_attendance.check_out:
                check_in_time = last_attendance.check_in
                hours_on_clock = (now - check_in_time).total_seconds() / 3600

                if hours_on_clock > FORGOT_THRESHOLD:
                    # Auto-close yesterday's and start today's
                    last_attendance.write({'check_out': check_in_time + datetime.timedelta(hours=8)})
                    env['hr.attendance'].create({'employee_id': employee.id, 'check_in': now})
                else:
                    # Normal Check-out
                    last_attendance.write({'check_out': now})
            
            # SCENARIO: Currently Checked Out
            else:
                env['hr.attendance'].create({
                    'employee_id': employee.id,
                    'check_in': now
                })
