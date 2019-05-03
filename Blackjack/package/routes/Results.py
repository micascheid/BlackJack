class RoundResult():
    def __init__(self, WL, winnings, tableValue):
        self.WL = WL
        self.winnings = winnings
        self.tableValue = tableValue
    def dictify(self):
        return {"WL": self.WL, "winnings": self.winnings, "tableValue": self.tableValue}

class HitResult():
    def __init__(self, total, result):
        self.total = total
        self.result = result
    def dictify(self):
        return {"total": self.total, "result": self.result}

class SplitResult:
    def __init__(self, split_alert, result):
        self.split_alert = split_alert
        self.result = result
    def dictify(self):
        return {"split_alert": self.split_alert, "result": self.result}