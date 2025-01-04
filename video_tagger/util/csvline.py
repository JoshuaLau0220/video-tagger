class CSVLine:
    def __init__(self, text, timestamp):
        self.text = text
        self.timestamp = timestamp

    def __str__(self):
        return f"{self.text},{self.timestamp}"
    
    def __repr__(self):
        return f"CSVLine(text={self.text}, timestamp={self.timestamp})"