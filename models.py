import random, sys
from util import write_csv_dicts
MAX_HOURS = 12 # targeted hours per worker
MIN_SHIFT_HOURS = 2 # 1日の最小勤務時間
MAX_SHIFT_HOURS = 8 # 1日の最大勤務時間
MAX_WORKERS = 4 # 同時間に働く最大労働者数

# Unit 1 hours
MAX_SLOTS =  MAX_HOURS
MIN_SHIFT_SLOTS = MIN_SHIFT_HOURS
MAX_SHIFT_SLOTS = MAX_SHIFT_HOURS

class TimeSlot:
  # id format: "月-13:00-14:00"
  def __init__(self, id):
    self.id = id
    self.available_workers = []
    self.worker = None
    self.slot_after = None
    self.day = id[:1]
    self.time = id[2:]

    self.sorted = False

  def __repr__(self):
    return "TimeSlot(" + self.id +")"

  def add_worker(self, worker):
    self.available_workers.append(worker)

  # Should be used after available_workers list is sorted
  def get_worker(self):
    if self.sorted == False:
      self.sort()
    if self.available_workers:
      highest_pref = self.available_workers[0].preference[self.id]
      worker_slots = self.available_workers[0].slots
      print(self.available_workers)
      input()
      worker_index = 0
      for i in range(len(self.available_workers)):
        if highest_pref - random.randint(0,1) < self.available_workers[i].preference[self.id]:
          break
        elif worker_slots - random.randint(0,2) > self.available_workers[i].slots:
          worker_slots = self.available_workers[i].slots
          worker_index = i

      return self.available_workers.pop(worker_index)

  def assign_worker(self, worker):
    self.worker = worker
    worker.slots += 1

  # 希望度合いによってソートする(high preference to low)
  def sort(self):
    self.available_workers.sort(key=lambda x: x.preference[self.id], reverse=True)
    self.sorted = True


class Worker:
  def __init__(self, id):
    self.id = id
    self.slots = 0
    self.preference = {}
    self.work_days = set()

  def __repr__(self):
    return self.id

  def update_pref(self, time_slot_id, pref):
    self.preference[time_slot_id] = pref

  def get_pref(self, time_slot_id):
    return self.preference[time_slot_id]

  def update_work_days(self, day):
    self.work_days.add(day)

  def can_work(self, time_slot):
    return self.slots < MAX_SLOTS and not (time_slot.day in self.work_days)

### other functions
def get_shift(start_time_slot, worker):
  shift = [start_time_slot]
  slot_after = start_time_slot.slot_after
  duration = 1
  while (duration < MAX_SHIFT_SLOTS and slot_after
        and duration + worker.slots <= MAX_HOURS):
    pref_after = worker.get_pref(slot_after.id)
    if pref_after > 0:
      shift.append(slot_after)
      slot_after = slot_after.slot_after
      duration += 1
    else:
      break
  return shift

def assign_shift(shift, worker):
  worker.update_work_days(shift[0].day)
  for time_slot in shift:
    time_slot.assign_worker(worker)

def get_min_max_worker_slots_diff(workers):
  slots = [workers[key].slots for key in workers]
  min_slots = min(slots)
  max_slots = max(slots)
  return max_slots - min_slots

def get_num_uncovered_shifts(time_slots):
  num_uncovered = 0
  for time_slot in time_slots:
    if time_slot.worker is None:
      num_uncovered += 1
  return num_uncovered

def get_all_times(time_slots):
  times = set()
  for time_slot in time_slots:
    times.add(time_slot.time)
  return times

def get_time_dict(times):
  time_dict = dict()
  for time in times:
    keys = ["time", "月", "火", "水", "木", "金", "土", "日"]
    vals = [time] + [None] * 7
    time_dict[time] = dict(zip(keys, vals))
  return time_dict

def update_time_dict(time_dict, time_slots):
  for time_slot in time_slots:
    time_dict[time_slot.time][time_slot.day] = str(time_slot.worker)

def write_result(time_slots, output):
  times = get_all_times(time_slots)
  time_dict = get_time_dict(times)
  update_time_dict(time_dict, time_slots)
  rows = [time_dict[time] for time in time_dict]
  rows.sort(key=lambda row: row["time"])
  headers = ["time", "月", "火", "水", "木", "金", "土", "日"]
  write_csv_dicts(output, headers, rows)

def print_summary(workers):
  print("====まとめ====")
  print("労働者名, 今週の総勤務時間")
  for name in workers:
    print(name, workers[name].slots)
