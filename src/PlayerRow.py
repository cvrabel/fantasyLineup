class PlayerRow:

	def __init__(self, playerName: str, currentPosition: str, positions: list, hasGameToday: bool, isInjured: bool, percentOwned: float, pr15: float):
		self.playerName = playerName
		self.currentPosition = currentPosition
		self.positions = positions
		self.hasGameToday = hasGameToday
		self.isInjured = isInjured 
		self.percentOwned = percentOwned
		self.pr15 = pr15

	def setCurrentPosition(self, newPosition):
		self.currentPosition = newPosition