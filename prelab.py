n = int(input("Enter an odd number: "))

if n % 2 == 0:
    print("Only odd numbers are allowed")
    exit()

square = [[0]*n for _ in range(n)]
i, j = n//2, n-1

for num in range(1, n*n + 1):
    if i < 0 and j == n:
        i, j = 0, n-2
    else:
        if i < 0: i = n-1
        if j == n: j = 0

    if square[i][j]:
        i += 1
        j -= 2
        continue

    square[i][j] = num
    i -= 1
    j += 1

for row in square:
    print(row)
