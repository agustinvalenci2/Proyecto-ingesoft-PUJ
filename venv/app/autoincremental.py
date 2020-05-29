import time
autoincremental=dict()
def increase(key):
	if autoincremental.get(key)==None:
		autoincremental[key]=1
	else:
		autoincremental[key]+=1
		return autoincremental[key]-1
newid=lambda : int(round(time.time() * 1000))
