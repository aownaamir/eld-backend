from datetime import datetime, timedelta

def format_time(dt):
    return dt.isoformat()

def simulate_trip(distance_miles, start_time, cycle_used):
    logs = []

    remaining_distance = distance_miles
    speed = 50  # mph assumption

    current_time = start_time
    distance_since_fuel = 0

    while remaining_distance > 0:
        day_log = []

        driving_today = 0
        duty_window_start = current_time

        # Pickup (on duty)
        day_log.append({
            "type": "on_duty",
            "start": format_time(current_time),
            "end": format_time(current_time + timedelta(hours=1))
        })
        current_time += timedelta(hours=1)



        # while driving_today < 11 and remaining_distance > 0:
        #     drive_hours = min(3, 11 - driving_today)

        #     distance_covered = drive_hours * speed
        #     distance_since_fuel += distance_covered
        #     remaining_distance -= distance_covered
            

        #     segment_end = current_time + timedelta(hours=drive_hours)

        #     day_log.append({
        #         "type": "driving",
        #         "start": format_time(current_time),
        #         "end": format_time(segment_end)
        #     })

        #     current_time = segment_end
        #     driving_today += drive_hours

        #     # 30 min break after 8 hours
        #     if driving_today >= 8:
        #         break_end = current_time + timedelta(minutes=30)
        #         day_log.append({
        #             "type": "off_duty",
        #             "start": format_time(current_time),
        #             "end": format_time(break_end)
        #         })
        #         current_time = break_end
        while driving_today < 11 and remaining_distance > 0:
            drive_hours = min(3, 11 - driving_today)

            distance_covered = drive_hours * speed
            remaining_distance -= distance_covered
            distance_since_fuel += distance_covered

            segment_end = current_time + timedelta(hours=drive_hours)

            # Driving segment
            day_log.append({
                "type": "driving",
                "start": format_time(current_time),
                "end": format_time(segment_end)
            })

            current_time = segment_end
            driving_today += drive_hours

            # ⛽ FUEL STOP (every ~1000 miles)
            if distance_since_fuel >= 1000:
                fuel_end = current_time + timedelta(minutes=30)

                day_log.append({
                    "type": "on_duty",
                    "start": format_time(current_time),
                    "end": format_time(fuel_end),
                    "note": "fuel_stop"
                })

                current_time = fuel_end
                distance_since_fuel = 0

            # 💤 30 min break after 8 hours driving
            if driving_today >= 8:
                break_end = current_time + timedelta(minutes=30)

                day_log.append({
                    "type": "off_duty",
                    "start": format_time(current_time),
                    "end": format_time(break_end)
                })

                current_time = break_end 




        # Sleep (10 hrs reset)
        sleep_end = current_time + timedelta(hours=10)
        day_log.append({
            "type": "sleeper",
            "start": format_time(current_time),
            "end": format_time(sleep_end)
        })

        current_time = sleep_end

        logs.append({
    "day": len(logs) + 1,
    "segments": day_log
})

    return logs
