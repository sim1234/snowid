import sdl2

TOOL_BUILD_MINER = "build_miner"
TOOL_BUILD_FACTORY = "build_factory"
TOOL_DEMOLISH = "demolish"

TOOL_SLOTS: list[str | None] = [
    TOOL_BUILD_MINER,
    TOOL_BUILD_FACTORY,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    TOOL_DEMOLISH,
]

KEY_SDLK_TO_SLOT: dict[int, int] = {
    sdl2.SDLK_1: 0,
    sdl2.SDLK_2: 1,
    sdl2.SDLK_3: 2,
    sdl2.SDLK_4: 3,
    sdl2.SDLK_5: 4,
    sdl2.SDLK_6: 5,
    sdl2.SDLK_7: 6,
    sdl2.SDLK_8: 7,
    sdl2.SDLK_9: 8,
    sdl2.SDLK_0: 9,
}
