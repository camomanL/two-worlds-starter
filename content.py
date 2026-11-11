"""Original towns, recipes and progression data."""
ITEMS = {
 'wood': {'name':'Driftwood','icon':'🪵','color':'#bb865a'},
 'berries': {'name':'Sunberries','icon':'🍓','color':'#ec6e84'},
 'ice': {'name':'Moon ice','icon':'🧊','color':'#85c8ea'},
 'fish': {'name':'Silverfin','icon':'🐟','color':'#7da6bd'},
 'stool': {'name':'Mushroom stool','icon':'🍄','color':'#e6ac7b','decor':True},
 'lantern': {'name':'Firefly lantern','icon':'🏮','color':'#efc66a','decor':True},
 'snowglobe': {'name':'Pocket blizzard','icon':'🔮','color':'#b5a3e6','decor':True},
 'banner': {'name':'Friendship bunting','icon':'🎏','color':'#ea9eab','decor':True},
 'parcel': {'name':'Neighbor parcel','icon':'🎁','color':'#9ab78b'},
}
RECIPES = {
 'stool': {'name':'Mushroom stool','cost':{'wood':2},'xp':8,'note':'A little seat for big ideas.'},
 'lantern': {'name':'Firefly lantern','cost':{'wood':2,'ice':2},'xp':15,'note':'Warm light, cool crystal. Better together.'},
 'snowglobe': {'name':'Pocket blizzard','cost':{'ice':2,'berries':2},'xp':15,'note':'A tiny winter for your sunny windowsill.'},
 'banner': {'name':'Friendship bunting','cost':{'wood':1,'berries':2},'xp':10,'note':'Every day can be a welcome party.'},
 'parcel': {'name':'Neighbor parcel','cost':{'wood':1,'fish':1,'ice':1},'xp':12,'note':'Deliver at the post office to build the Lantern Festival.'},
}
WORLDS = {
 'snoopy': {'name':'Snoopyland','subtitle':'SUNSHINE HARBOR','resident':'Mabel',
  'greeting':'Two towns, one festival. Bring a little sunshine to our snowy neighbors.',
  'nodes':[{'id':'sun-wood','item':'wood','x':240,'y':300,'qty':2},
           {'id':'sun-berries','item':'berries','x':760,'y':300,'qty':3}],
  'fish':[320,540],'workshop':[540,250],'post':[840,520],'portal':[1050,385],'home':[175,465]},
 'penguin': {'name':'Penguinland','subtitle':'AURORA COVE','resident':'Pip',
  'greeting':'The aurora looks brighter with friends. Our moon ice makes the best lanterns.',
  'nodes':[{'id':'snow-ice','item':'ice','x':735,'y':300,'qty':3},
           {'id':'snow-wood','item':'wood','x':240,'y':300,'qty':2}],
  'fish':[320,540],'workshop':[540,250],'post':[840,520],'portal':[1050,385],'home':[175,465]},
}
QUESTS = [
 {'id':'berry-trail','name':'A berry good beginning','text':'Pick a sunberry bush in Snoopyland.','stat':'gather_berries','goal':3,'coins':15,'xp':15},
 {'id':'polar-hello','name':'Hello, other side','text':'Take the sky ferry to Penguinland.','stat':'visits_penguin','goal':1,'coins':20,'xp':20},
 {'id':'first-catch','name':'Something fishy','text':'Catch a silverfin at either pond.','stat':'fish_caught','goal':1,'coins':15,'xp':15},
 {'id':'warm-glow','name':'A little warm, a little cool','text':'Craft a firefly lantern from wood and moon ice.','stat':'craft_lantern','goal':1,'coins':25,'xp':25},
 {'id':'neighborly','name':'Special delivery','text':'Craft and deliver a neighbor parcel.','stat':'deliveries','goal':1,'coins':25,'xp':25},
 {'id':'nest','name':'Make yourself at home','text':'Place a crafted decoration in your room.','stat':'decorated','goal':1,'coins':10,'xp':15},
 {'id':'kindness','name':'Pass a little joy along','text':'Give a resource to another nearby player.','stat':'gifts','goal':1,'coins':15,'xp':15},
]
EMOTES = ['wave','heart','dance','snow']
PROJECT_GOAL = 20
