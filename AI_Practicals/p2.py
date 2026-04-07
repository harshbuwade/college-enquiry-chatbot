def water_jug_dfs(m, n, goal):
    visited = set()
    found = False   # <-- FLAG to stop DFS after goal

    def dfs(j1, j2):
        nonlocal found

        if found:
            return

        if (j1, j2) in visited:
            return
        visited.add((j1, j2))

        print(j1, j2)

        # Goal condition
        if j1 == goal or j2 == goal:
            print("Goal Reached")
            found = True
            return

        # Fill Jug1
        if j1 < m:
            dfs(m, j2)

        # Fill Jug2
        if j2 < n:
            dfs(j1, n)

        # Empty Jug1
        if j1 > 0:
            dfs(0, j2)

        # Empty Jug2
        if j2 > 0:
            dfs(j1, 0)

        # Pour Jug1 → Jug2
        if j1 > 0 and j2 < n:
            t = min(j1, n - j2)
            dfs(j1 - t, j2 + t)

        # Pour Jug2 → Jug1
        if j2 > 0 and j1 < m:
            t = min(j2, m - j1)
            dfs(j1 + t, j2 - t)

    dfs(0, 0)


# -------- INPUT --------
m = int(input("Enter capacity of Jug 1: "))
n = int(input("Enter capacity of Jug 2: "))
goal = int(input("Enter goal amount: "))

water_jug_dfs(m, n, goal)
