from turing_game.entities.base_entity import BaseEntity


def test_base_entity_init():
    entity = BaseEntity(10, 20, 30, 40)
    assert entity.pos.x == 10
    assert entity.pos.y == 20
    assert entity.rect.width == 30
    assert entity.rect.height == 40
    assert entity.vel.x == 0
    assert entity.vel.y == 0


def test_base_entity_sync_rect():
    entity = BaseEntity(0, 0, 10, 10)
    entity.pos.x = 15.6
    entity.pos.y = -4.2
    entity.sync_rect()
    assert entity.rect.x == 16  # round(15.6)
    assert entity.rect.y == -4  # round(-4.2)
