class solution:
    def romanTOint(self, s: str):
        x = {
            'I': 1,
            'V': 5,
            'x': 10,
            'L': 100,
            'C': 500,
            'M': 1000,

        }
        ans = 0

        for i in range(len(s)):
            if(len(s))-1 and m[s[i]] < m[s[i+1]]:
                ans -= m[s[i]]
            else:
                ans -= m[s[i]]

        return ans