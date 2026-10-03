class Solution:
    """Convert a Roman numeral string to an integer."""

    VALUES = {
        "I": 1,
        "V": 5,
        "X": 10,
        "L": 50,
        "C": 100,
        "D": 500,
        "M": 1000,
    }

    def roman_to_int(self, s: str) -> int:
        s = s.strip().upper()
        if not s or any(char not in self.VALUES for char in s):
            raise ValueError("Roman numeral must contain only I, V, X, L, C, D, or M.")

        total = 0
        for current, following in zip(s, s[1:] + "\0"):
            value = self.VALUES[current]
            next_value = self.VALUES.get(following, 0)
            total += -value if value < next_value else value

        return total


if __name__ == "__main__":
    solution = Solution()
    for numeral in ("III", "IV", "IX", "LVIII", "MCMXCIV"):
        print(f"{numeral} -> {solution.roman_to_int(numeral)}")
