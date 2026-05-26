# Collision Tracking Limitation in Dynamic Obstacle Evaluation

## ⚠️ Issue Identified

The dynamic obstacle evaluation **does NOT track static vs dynamic collisions separately**.

## Current Implementation

In `benchmark_comparison.py` (lines 201-211):

```python
# Count collisions - properly validate bounds and exclude start/goal
collisions = 0
for step in path:
    # Exclude start and goal positions from collision counting
    if step == env.goal or step == env.start:
        continue
    # Validate bounds before accessing grid
    if (0 <= step[0] < len(env.grid) and 
        0 <= step[1] < len(env.grid[0])):
        if env.grid[step[0]][step[1]] == 1:
            collisions += 1
```

**Problems:**
1. Only tracks **total collisions** (single metric)
2. Checks final path against **final grid state**
3. Does NOT distinguish static vs dynamic obstacles
4. Does NOT simulate obstacle movement during execution
5. Does NOT count collisions that occur when obstacles move into planned positions

## What Should Be Tracked

For proper dynamic obstacle evaluation:

### 1. Static Collisions (`collisions_static`)
- Collisions with obstacles that were present in the initial grid
- Obstacles that were there when path was planned

### 2. Dynamic Collisions (`collisions_dynamic`)
- Collisions with obstacles that moved into the path during execution
- Obstacles that appeared after path planning
- Obstacles that moved from one position to block the planned path

### 3. Real-Time Collision Detection
- Check for collisions **during path execution** (not just at the end)
- Simulate obstacle movement step-by-step
- Count collisions when obstacles move into planned positions

## Comparison with Other Scripts

**`run_initial_benchmarks.py`** (lines 49-50, 143-144):
```python
collisions_static = 0
collisions_dynamic = 0
# ...
return {
    "collisions_static": collisions_static,
    "collisions_dynamic": collisions_dynamic,
}
```

✅ **Tracks separately** (though implementation may still need improvement)

**`benchmark_comparison.py`**:
```python
collisions = 0  # Single metric
# ...
return {
    "collisions": collisions,  # No distinction
}
```

❌ **Only tracks total** - missing dynamic collision data

## Impact on Results

The current results show:
- **"All Methods: 0 collisions"**

But this doesn't tell us:
- How many collisions were with static obstacles?
- How many collisions were with dynamic obstacles?
- Did obstacles move into the path during execution?
- Were collisions avoided through replanning?

## What's Needed

### Option 1: Update `benchmark_comparison.py`

1. **Track initial static obstacles:**
   ```python
   initial_static_obstacles = set()
   for i in range(len(env.grid)):
       for j in range(len(env.grid[0])):
           if env.grid[i][j] == 1:
               initial_static_obstacles.add((i, j))
   ```

2. **Simulate execution with obstacle movement:**
   ```python
   collisions_static = 0
   collisions_dynamic = 0
   current_pos = path[0]
   
   for planned_step in path[1:]:
       # Move obstacles (if moving_obstacles=True)
       if moving_obstacles:
           # Simulate obstacle movement
           move_obstacles(env)
       
       # Check for collision
       if env.grid[planned_step[0]][planned_step[1]] == 1:
           if planned_step in initial_static_obstacles:
               collisions_static += 1
           else:
               collisions_dynamic += 1  # Obstacle moved here
   ```

3. **Return separate metrics:**
   ```python
   return {
       "collisions_static": collisions_static,
       "collisions_dynamic": collisions_dynamic,
       "collisions": collisions_static + collisions_dynamic,
   }
   ```

### Option 2: Use Existing Script

Use `run_initial_benchmarks.py` which already tracks separately (though may need verification for dynamic obstacles).

## Recommendation

**Priority: HIGH** - This is important for proper evaluation because:

1. **Objective #1** is about dynamic obstacle avoidance
2. Need to show **how many dynamic collisions occurred**
3. Need to demonstrate **effectiveness of replanning**
4. Results should distinguish **static vs dynamic** obstacle handling

## Next Steps

1. **Update `benchmark_comparison.py`** to track collisions separately
2. **Re-run dynamic obstacle evaluation** with proper collision tracking
3. **Update results documentation** with static vs dynamic collision data
4. **Add to thesis**: Show dynamic collision avoidance effectiveness

---

**Status**: ⚠️ **LIMITATION** - Dynamic collisions are not tracked separately in current evaluation
