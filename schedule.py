import csv, sys, argparse, random, copy
from models import *
from util import *

def get_arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument("input", help="input.csv")
  parser.add_argument("output", help="output.csv")
  parser.add_argument("-i", "--iterations", type=int, default=1000,
                      help="Number of iterations")
  return parser.parse_args()

def schedule_shifts(headers, rows):
  workers = {}
  time_slots = {}
  for name in headers[1:]:
    workers[name] = Worker(name)

  update_time_slots_and_workers(rows, time_slots, workers)
  time_slot_list = get_shuffled_time_slots(time_slots)

  for time_slot in time_slot_list:
    if not time_slot.worker and time_slot.available_workers:
      while time_slot.available_workers:
        worker = time_slot.get_worker()
        if worker.can_work(time_slot):
          shift = get_shift(time_slot, worker)
          if len(shift) >= MIN_SHIFT_SLOTS:
            break

      if worker:
        duration = len(shift)
        if duration > MAX_SHIFT_SLOTS - 3:
          duration = random.randrange(6, duration + 1)
        assign_shift(shift[:duration], worker)

  days = {"月": 1, "火": 2, "水": 3, "木": 4, "金": 5, "土": 6, "日": 7}
  time_slot_list.sort(key=lambda ts: (days[ts.day], ts.time))

  res = {"time_slots": time_slot_list, "workers": workers}
  return res

def update_time_slots_and_workers(rows, time_slots, workers):
  prev_id = None
  for row in rows:
    current_id = row["time"]

    update_dict(time_slots, current_id, TimeSlot(current_id))

    if (prev_id and time_slots[prev_id].day == time_slots[current_id].day):
      time_slots[prev_id].slot_after = time_slots[current_id]

    for name in workers:
      pref = int(row[name])
      worker = workers[name]
      worker.update_pref(current_id, pref)
      # シフト割り当て
      if pref > 0:
        time_slots[current_id].add_worker(worker)
    prev_id = current_id

def get_shuffled_time_slots(time_slots):
  priority = range(1,8)
  days = ["月", "火", "水", "木", "金", "土", "日"]
  random.shuffle(days)
  day_to_priority = dict(zip(days, priority))
  time_slot_list = dict_val_to_list(time_slots)
  time_slot_list.sort(key=lambda ts: (day_to_priority[ts.day], ts.time))
  return time_slot_list

def repeat_scheduling(headers, rows, iterations):
  best_schedule = schedule_shifts(headers, rows)
  best_uncovered = get_num_uncovered_shifts(best_schedule["time_slots"])
  best_slots_diff = get_min_max_worker_slots_diff(best_schedule["workers"])

  # 試行回数(iteration)
  for i in range(iterations):
    current_schedule = schedule_shifts(headers, rows)
    current_uncovered = get_num_uncovered_shifts(current_schedule["time_slots"])
    current_slots_diff = get_min_max_worker_slots_diff(current_schedule["workers"])
    if current_uncovered <= best_uncovered and current_slots_diff <= best_slots_diff:
      best_schedule = current_schedule
      best_uncovered = current_uncovered
      best_slots_diff = current_slots_diff

  return best_schedule

if __name__ == '__main__':
  args = get_arguments()
  headers = get_headers(args.input)
  rows = get_list_of_dicts(args.input)
  iterations = int(args.iterations)
  schedule = repeat_scheduling(headers, rows, iterations)
  write_result(schedule["time_slots"], args.output)
  print_summary(schedule["workers"])
