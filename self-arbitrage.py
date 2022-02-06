import copy
import numpy as np
import pygame
import pygame_gui
from pygame_gui import UIManager, PackageResource
from pygame_gui.elements import UIButton
from pygame_gui.elements import UILabel
from pygame_gui.elements import UIPanel
from pygame_gui.elements import UITextBox

is_running = False

pygame.init()

pygame.display.set_caption('Self-Arbitrage')
window_surface = pygame.display.set_mode((800, 600))

background = pygame.Surface((800, 600))
#background.fill(pygame.Color('#eae9e9'))
background.fill(pygame.Color('#A5AAAF'))

manager = UIManager((800, 600)) #, 'data/themes/quick_theme.json')
#print(manager.get_theme())

creation_button = UIButton(text= "Split Timeline", tool_tip_text = 'Copy the current timeline into two',
							relative_rect=pygame.Rect(300,500,200,50),
							manager = manager)
creation_button.hide()


def price_change(world,change):   # the share price varies in time
	world.ws.shareprice = round(world.ws.shareprice + 5*change+1)
	if world.ws.shareprice < 1:               # the share price cannot be 0 or negative
		world.ws.shareprice = 1
	world.update_share_price()


class Timeline_tracker():
	def __init__ (self,active_timeline='both'):
		self.active_timeline = active_timeline
		self.day = 1
		self.total_days = 7
		self.game_end = False
		self.start_days()

	def start_days(self):
		try:
			self.day_button.kill()
		except:
			pass
		finally:
			self.day_button = UIButton(text = "Next Day", tool_tip_text = 'Advances time',
					relative_rect=pygame.Rect(320,35,160,50),
					manager = manager)
			self.update_day()

	def update_day(self):
		if self.game_end == True:
			self.day_button.kill()
			self.day_button = UIButton(text = "Game End", tool_tip_text = 'Cash out your money',
							relative_rect=pygame.Rect(320,35,160,50),
							manager = manager)
			self.day_button.disable()
		try:
			self.day_label.kill()
		except:
			pass
		finally:
			self.day_label = UILabel(text = "Day "+str(self.day)+"/"+str(self.total_days),
						relative_rect=pygame.Rect(600,35,120,50),
						manager = manager)


tt = Timeline_tracker()

class WorldState():
	def __init__(self, money = 500,shareprice=50, shares = 0):
		self.money = money
		self.shareprice = shareprice
		self.shares = shares

	def __str__(self):
		return str(self.money)

class World():
	def __init__(self, worldstate,side):
		self.ws = copy.deepcopy(worldstate)
		self.side = side
		if self.side == "left":
			self.left = 100
		elif self.side == "right":
			self.left = 500
		else:
			raise ValueError("weird side assigned")
		self.top = 100
		self.box_width = 200
		self.information_panel = UIPanel(relative_rect=pygame.Rect(self.left,self.top,self.box_width+6,310),
							starting_layer_height = 0,
							manager=manager)
		self.draw()

	def draw(self):
		self.update()
		self.infobox = UITextBox(html_text= "Information",
								relative_rect=pygame.Rect(0,0,self.box_width,50), # left,top,width,height
								container = self.information_panel,
								manager=manager)

		self.buyshares = UIButton(relative_rect=pygame.Rect(40,200, 120, 50),
									text='Buy shares', tool_tip_text = 'Purchase diversified stock',
									container = self.information_panel,						
									manager=manager)
		self.sellshares = UIButton(relative_rect=pygame.Rect(40,250, 120, 50),
									text='Sell shares', tool_tip_text = 'Set a sale of diversified stock',
									container = self.information_panel,						
									manager=manager)
		self.timeline_button = UIButton(relative_rect=pygame.Rect(self.left, self.top+400, self.box_width, 50),
							text="Drop timeline", tool_tip_text = 'Delete selected timeline',						
							manager=manager)	
	
	def redraw(self):
		self.information_panel.kill()
		self.timeline_button.kill()
		self.information_panel = UIPanel(relative_rect=pygame.Rect(self.left,self.top,self.box_width+6,310),
							starting_layer_height = 0,
							manager=manager)
		self.draw()

	def update(self):
		self.update_money()
		self.update_share_price()

	def update_share_price(self):
		try:
			self.shareprice_box.kill()
		except:
			pass
		finally:
			self.shareprice_box = UITextBox(html_text= "Share price: "+str(self.ws.shareprice),
				container = self.information_panel,				
				relative_rect=pygame.Rect(0,150,self.box_width,50),
				manager=manager)

	def update_money(self):
		try:
			self.moneybox.kill()
			self.sharecount_box.kill()
		except:
			pass
		finally:
			self.moneybox = UITextBox(html_text= "Money: "+str(self.ws.money),
										relative_rect=pygame.Rect(0,50,self.box_width,50),
										container = self.information_panel,
										manager=manager)
			self.sharecount_box = UITextBox(html_text= "Shares: "+str(self.ws.shares),
										container = self.information_panel,
										relative_rect=pygame.Rect(0,100,self.box_width,50),
										manager=manager)
	def show_score(self):
		score = w.ws.money + w.ws.shares * w.ws.shareprice
		if tt.game_end == True:
			try:
				self.score_label.kill()
			except:
				pass
			finally:
				if tt.active_timeline == "both":
					self.score_label = UILabel(text = "Score: "+str(score),
								relative_rect=pygame.Rect(self.left+3,self.top+310,200,50),
								manager = manager)
				elif tt.active_timeline == self.side:
					self.score_label = UILabel(text = "Score: "+str(score),
								relative_rect=pygame.Rect(303,self.top+310,200,50),
								manager = manager)
		else:
			try:
				self.score_label.hide()
			except:
				pass

	def return_state(self):
		return self.ws

	def drop(self):
		self.information_panel.hide()
		if tt.game_end == True:
			self.score_label.hide()
		if self.side == "left":
			tt.active_timeline = "right"
			world_right.information_panel.set_position(pygame.Rect(300,100,self.box_width+6,310))
			world_right.show_score()
		elif self.side == 'right':
			tt.active_timeline = "left"
			world_left.information_panel.set_position(pygame.Rect(300,100,self.box_width+6,310))
			world_left.show_score()
		else:
			raise ValueError('side shenanigans on drop')
		world_right.timeline_button.hide()
		world_left.timeline_button.hide()
		creation_button.show()

	def create(self):
		if self.side == "left":
			self.ws = copy.deepcopy(world_right.return_state())
		elif self.side == 'right':
			self.ws = copy.deepcopy(world_left.return_state())
		else:
			raise ValueError('side shenanigans on create')
		world_right.timeline_button.show()
		world_left.timeline_button.show()
		self.update()
		self.information_panel.show()
		creation_button.hide()
		tt.active_timeline = "both"


restart_button = UIButton(text= "Restart Game", tool_tip_text = 'Start again from the beginning',
							relative_rect=pygame.Rect(75,35,140,50),
							manager = manager)
restart_button.hide()

stats_start = WorldState()		
world_left = World(stats_start,side="left")
world_right = World(stats_start,side="right")
worlds = [world_left,world_right]

for w in [world_left]:
	w.drop()


clock = pygame.time.Clock()
is_running = True


while is_running:
	time_delta = clock.tick(60)/1000.0
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			is_running = False

		if event.type == pygame_gui.UI_BUTTON_PRESSED:
			if event.ui_element == creation_button:
				try:
					if tt.active_timeline == "left":
						world_right.create()
						for w in worlds:
							w.show_score()
					elif tt.active_timeline == 'right':
						world_left.create()
						for w in worlds:
							w.show_score()
					else:
						raise ValueError('timeline shenanigans - '+tt.active_timeline)
				except NameError:
					print('NameError for',tt.active_timeline)
				finally:
					world_left.information_panel.set_position(pygame.Rect(world_left.left,world_left.top,206,310))
					world_right.information_panel.set_position(pygame.Rect(world_right.left,world_right.top,206,310))

			elif event.ui_element == tt.day_button:
				if tt.game_end == False:
					change = np.random.normal()
					for w in worlds:
						price_change(w,change)
					tt.day += 1
					if tt.day >= tt.total_days:
						tt.game_end = True
						restart_button.show()	# TODO: Enable restart button and make it actually work properly
						for w in worlds:
							w.show_score()
					tt.update_day()

			elif event.ui_element == restart_button:
				world_left.ws = WorldState()
				world_right.ws = WorldState()
				tt.game_end = False
				tt.start_days()
				worlds = [world_left,world_right]
				tt.day = 1
				tt.update_day()
				for w in worlds:
					w.show_score()
					w.redraw()
				restart_button.hide()
				creation_button.hide()

			else:
				for w in worlds:
					if event.ui_element == w.buyshares and w.ws.money >= w.ws.shareprice:
						w.ws.shares += 1
						w.ws.money -= w.ws.shareprice
						w.update_money()
					elif event.ui_element == w.sellshares and w.ws.shares > 0:
						w.ws.shares -= 1
						w.ws.money += w.ws.shareprice
						w.update_money()
					elif event.ui_element == w.timeline_button:
						w.drop()
						for w in worlds:
							w.show_score()					






		manager.process_events(event)

	manager.update(time_delta)

	window_surface.blit(background, (0, 0))
	manager.draw_ui(window_surface)

	pygame.display.update()