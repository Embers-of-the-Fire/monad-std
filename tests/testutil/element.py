class Element:
    value: int
    id: int

    def __init__(self, value, vid):
        self.value = value
        self.id = vid

    def __gt__(self, other: "Element") -> bool:
        if not isinstance(other, Element):
            raise TypeError("Element can only compare with another Element.")
        return self.value > other.value

    def __lt__(self, other: "Element") -> bool:
        if not isinstance(other, Element):
            raise TypeError("Element can only compare with another Element.")
        return self.value < other.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Element):
            raise TypeError("Element can only compare with another Element.")
        return self.value == other.value

    def same_as(self, other: "Element") -> bool:
        return self.value == other.value and self.id == other.id
