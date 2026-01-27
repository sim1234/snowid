from gamepart.physics.category import Category, cat_all, cat_none  # noqa: F401

cat_terrain = Category()
cat_player = Category()
cat_enemy = Category()
cat_player_projectile = Category()
cat_enemy_projectile = Category()
cat_collectible = Category()

cat_terrain_collide = cat_all
cat_player_collide = (
    cat_terrain + cat_enemy_projectile + cat_collectible + cat_player + cat_enemy
)
cat_enemy_collide = cat_terrain + cat_player_projectile + cat_enemy + cat_player
cat_player_projectile_collide = cat_terrain + cat_enemy
cat_enemy_projectile_collide = cat_terrain + cat_player
cat_collectible_collide = cat_terrain + cat_player
