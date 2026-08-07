# Six hints for a stronger solution

1. Build a simple instruction parser that recognizes the task based on the verb and extracts every mentioned colour-object pair.

2. Locate the robot and the named objects on the grid, then add their relative row and column offsets as features.

3. Add the robot's direction, the object directly in front and the `carrying` value as features (to recognize when to pick up or drop).

4. For put-next missions, classify each snapshot as approaching the source, picking it up, carrying it or ready to drop it.

5. For each `robot_id`, count which object-colour pairs are often present for this robot, and use them as features.

6. Train a separate small six-action classifier for each robot on these features and compare validation accuracy per robot.
