PLATFORM_SPECIAL: dict[str, frozenset[str]] = {
    "xbox":    frozenset(),
    "steam":   frozenset({"_"}),
    "roblox":  frozenset({"_"}),
    "discord": frozenset({"_", "."}),
}


def allowed_special(platforms: list[str]) -> frozenset[str]:
    if not platforms:
        return frozenset()
    sets = [PLATFORM_SPECIAL.get(p, frozenset()) for p in platforms]
    result = sets[0]
    for s in sets[1:]:
        result = result & s
    return result


def semi_supported(platforms: list[str]) -> bool:
    return bool(allowed_special(platforms))
