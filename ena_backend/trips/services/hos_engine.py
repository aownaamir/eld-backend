from datetime import datetime, timedelta


def format_time(dt):
    return dt.isoformat()


def clamp_segment(start, end, day_end):
    if end > day_end:
        return start, day_end, True
    return start, end, False


def simulate_trip(distance_miles, start_time, cycle_used):
    logs = []

    remaining_distance = distance_miles
    speed = 50
    distance_since_fuel = 0

    # Keep actual start time (NOT forcing midnight)
    current_time = start_time

    while remaining_distance > 0:
        day_log = []

        # Define day boundaries
        day_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(hours=24)

        # ✅ FIX: Fill initial off-duty if day starts before current_time
        if current_time > day_start:
            day_log.append({
                "type": "off_duty",
                "start": format_time(day_start),
                "end": format_time(current_time)
            })

        driving_today = 0

        # -------------------
        # PICKUP (1 hour)
        # -------------------
        raw_end = current_time + timedelta(hours=1)
        seg_start, seg_end, _ = clamp_segment(current_time, raw_end, day_end)

        day_log.append({
            "type": "on_duty",
            "start": format_time(seg_start),
            "end": format_time(seg_end),
            "note": "pickup"
        })

        current_time = seg_end
        if current_time >= day_end:
            logs.append({
                "day": len(logs) + 1,
                "segments": fill_day(day_log, current_time, day_end)
            })
            current_time = day_end
            continue

        # -------------------
        # DRIVING LOOP
        # -------------------
        while driving_today < 11 and remaining_distance > 0:
            drive_hours = min(3, 11 - driving_today)

            distance_covered = drive_hours * speed
            remaining_distance -= distance_covered
            distance_since_fuel += distance_covered

            raw_end = current_time + timedelta(hours=drive_hours)
            seg_start, seg_end, _ = clamp_segment(current_time, raw_end, day_end)

            day_log.append({
                "type": "driving",
                "start": format_time(seg_start),
                "end": format_time(seg_end)
            })

            current_time = seg_end
            driving_today += drive_hours

            if current_time >= day_end:
                break

            # ⛽ Fuel stop
            if distance_since_fuel >= 1000:
                raw_end = current_time + timedelta(minutes=30)
                seg_start, seg_end, _ = clamp_segment(current_time, raw_end, day_end)

                day_log.append({
                    "type": "on_duty",
                    "start": format_time(seg_start),
                    "end": format_time(seg_end),
                    "note": "fuel"
                })

                current_time = seg_end
                distance_since_fuel = 0

                if current_time >= day_end:
                    break

            # 💤 Break after 8 hrs
            if driving_today >= 8:
                raw_end = current_time + timedelta(minutes=30)
                seg_start, seg_end, _ = clamp_segment(current_time, raw_end, day_end)

                day_log.append({
                    "type": "off_duty",
                    "start": format_time(seg_start),
                    "end": format_time(seg_end)
                })

                current_time = seg_end

                if current_time >= day_end:
                    break

        # -------------------
        # SLEEP (10 hours)
        # -------------------
        if remaining_distance > 0:
            raw_end = current_time + timedelta(hours=10)
            seg_start, seg_end, _ = clamp_segment(current_time, raw_end, day_end)

            day_log.append({
                "type": "sleeper",
                "start": format_time(seg_start),
                "end": format_time(seg_end)
            })

            current_time = seg_end

        # -------------------
        # Fill remaining day to 24:00
        # -------------------
        day_log = fill_day(day_log, current_time, day_end)

        logs.append({
            "day": len(logs) + 1,
            "segments": day_log
        })

        current_time = day_end

    return logs


def fill_day(day_log, current_time, day_end):
    if current_time < day_end:
        day_log.append({
            "type": "off_duty",
            "start": format_time(current_time),
            "end": format_time(day_end)
        })
    return day_log