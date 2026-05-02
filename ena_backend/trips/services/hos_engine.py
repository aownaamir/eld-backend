from datetime import datetime, timedelta


def format_time(dt):
    return dt.isoformat()


def is_valid_segment(start, end):
    return (end - start).total_seconds() > 60


def clamp_segment(start, end, day_end):
    if end > day_end:
        return start, day_end, True
    return start, end, False


def fill_day(day_log, current_time, day_end):
    if current_time < day_end:
        seg = {
            "type": "off_duty",
            "start": format_time(current_time),
            "end": format_time(day_end)
        }
        if is_valid_segment(current_time, day_end):
            day_log.append(seg)
    return day_log


def simulate_trip(distance_miles, start_time, cycle_used):
    logs = []
    remaining_distance = distance_miles
    speed = 55
    distance_since_fuel = 0
    cycle_hours = float(cycle_used)
    current_time = start_time
    pickup_done = False
    dropoff_done = False

    def add_cycle_hours(ch, start, end):
        return ch + (end - start).total_seconds() / 3600

    while remaining_distance > 0 or not dropoff_done:
        day_log = []
        day_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(hours=24)

        # Initial off-duty from midnight to current time
        if current_time > day_start:
            if is_valid_segment(day_start, current_time):
                day_log.append({
                    "type": "off_duty",
                    "start": format_time(day_start),
                    "end": format_time(current_time)
                })

        driving_today = 0
        break_taken = False
        window_start = current_time  # 14hr window start

        
        # 70-HOUR CYCLE CHECK        
        if cycle_hours >= 70:
            reset_end = current_time + timedelta(hours=34)

            while current_time < reset_end:
                seg_day_end = current_time.replace(
                    hour=0, minute=0, second=0, microsecond=0
                ) + timedelta(hours=24)
                seg_end = min(reset_end, seg_day_end)

                if is_valid_segment(current_time, seg_end):
                    day_log.append({
                        "type": "sleeper",
                        "start": format_time(current_time),
                        "end": format_time(seg_end),
                        "note": "34hr_reset"
                    })

                if seg_end == seg_day_end and seg_end < reset_end:
                    logs.append({"day": len(logs) + 1,"segments": merge_segments(day_log)})
                    day_log = []
                    current_time = seg_day_end
                    day_start = current_time
                    day_end = day_start + timedelta(hours=24)
                else:
                    current_time = seg_end

            cycle_hours = 0
            day_log = fill_day(day_log, current_time, day_end)
            logs.append({"day": len(logs) + 1,"segments": merge_segments(day_log)})
            current_time = day_end
            continue


        # PICKUP (once)
        if not pickup_done:
            raw_end = current_time + timedelta(hours=1)
            seg_start, seg_end, _ = clamp_segment(current_time, raw_end, day_end)

            if is_valid_segment(seg_start, seg_end):
                day_log.append({
                    "type": "on_duty",
                    "start": format_time(seg_start),
                    "end": format_time(seg_end),
                    "note": "pickup"
                })
                cycle_hours = add_cycle_hours(cycle_hours, seg_start, seg_end)

            current_time = seg_end
            pickup_done = True

            if current_time >= day_end:
                logs.append({
                    "day": len(logs) + 1,
                    "segments": fill_day(day_log, current_time, day_end)
                })
                current_time = day_end
                continue

        
        # DRIVING LOOP
        while driving_today < 11 and remaining_distance > 0:

            if cycle_hours >= 70:
                break

            # 14hr window check
            window_used = (current_time - window_start).total_seconds() / 3600
            if window_used >= 14:
                break

            drive_hours = min(3, 11 - driving_today)
            drive_hours = min(drive_hours, 14 - window_used)

            distance_covered = drive_hours * speed
            remaining_distance -= distance_covered #############################################
            distance_since_fuel += distance_covered

            raw_end = current_time + timedelta(hours=drive_hours)
            seg_start, seg_end, _ = clamp_segment(current_time, raw_end, day_end)

            if is_valid_segment(seg_start, seg_end):
                day_log.append({
                    "type": "driving",
                    "start": format_time(seg_start),
                    "end": format_time(seg_end)
                })
                cycle_hours = add_cycle_hours(cycle_hours, seg_start, seg_end)

            current_time = seg_end
            driving_today += (seg_end - seg_start).total_seconds() / 3600

            if current_time >= day_end:
                break


            # Fuel stop every 1000 miles
            if distance_since_fuel >= 1000:
                raw_end = current_time + timedelta(minutes=30)
                seg_start, seg_end, _ = clamp_segment(current_time, raw_end, day_end)

                if is_valid_segment(seg_start, seg_end):
                    day_log.append({
                        "type": "on_duty",
                        "start": format_time(seg_start),
                        "end": format_time(seg_end),
                        "note": "fuel"
                    })
                    cycle_hours = add_cycle_hours(cycle_hours, seg_start, seg_end)

                current_time = seg_end
                distance_since_fuel = 0

                if current_time >= day_end:
                    break


            # 30-min break after 8hrs driving (once per day)
            if driving_today >= 8 and not break_taken:
                raw_end = current_time + timedelta(minutes=30)
                seg_start, seg_end, _ = clamp_segment(current_time, raw_end, day_end)

                if is_valid_segment(seg_start, seg_end):
                    day_log.append({
                        "type": "off_duty",
                        "start": format_time(seg_start),
                        "end": format_time(seg_end),
                        "note": "break"
                    })

                current_time = seg_end
                break_taken = True

                if current_time >= day_end:
                    break



        # DROPOFF (once, when trip done)
        if remaining_distance <= 0 and not dropoff_done:
            raw_end = current_time + timedelta(hours=1)
            seg_start, seg_end, _ = clamp_segment(current_time, raw_end, day_end)

            if is_valid_segment(seg_start, seg_end):
                day_log.append({
                    "type": "on_duty",
                    "start": format_time(seg_start),
                    "end": format_time(seg_end),
                    "note": "dropoff"
                })
                cycle_hours = add_cycle_hours(cycle_hours, seg_start, seg_end)

            current_time = seg_end
            dropoff_done = True


        # 70HR EXCEEDED to 34hr reset
        if cycle_hours >= 70:
            raw_end = current_time + timedelta(hours=34)
            seg_start, seg_end, _ = clamp_segment(current_time, raw_end, day_end)

            if is_valid_segment(seg_start, seg_end):
                day_log.append({
                    "type": "sleeper",
                    "start": format_time(seg_start),
                    "end": format_time(seg_end),
                    "note": "34hr_reset"
                })

            current_time = seg_end
            cycle_hours = 0


        # 10hr sleeper between days
        elif not dropoff_done:
            raw_end = current_time + timedelta(hours=10)
            seg_start, seg_end, _ = clamp_segment(current_time, raw_end, day_end)

            if is_valid_segment(seg_start, seg_end):
                day_log.append({
                    "type": "sleeper",
                    "start": format_time(seg_start),
                    "end": format_time(seg_end)
                })

            current_time = seg_end

        # remaining day with off_duty
        day_log = fill_day(day_log, current_time, day_end)

        logs.append({"day": len(logs) + 1,"segments": merge_segments(day_log)})
        current_time = day_end

        if dropoff_done:
            break

    return logs



def merge_segments(segments):
    if not segments:
        return segments
    
    merged = [segments[0].copy()]
    
    for seg in segments[1:]:
        last = merged[-1]
        if seg["type"] == last["type"] and seg.get("note") == last.get("note"):
            last["end"] = seg["end"]
        else:
            merged.append(seg.copy())
    
    return merged