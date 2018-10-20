# Player per game stats for a season
class PlayerRow:

	def __init__(self, playerName: str, positions: list, hasGameToday: bool, isInjured: bool, percentOwned: float, pr15: float):
		self.playerName = playerName
		self.positions = positions
		self.hasGameToday = hasGameToday
		self.isInjured = isInjured
		self.percentOwned = percentOwned
		self.pr15 = pr15