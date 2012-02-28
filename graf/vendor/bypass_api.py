import urllib,base64

class bypassClient():
  def __init__(self, key):
    self.__key = key

  def decode( self, image, timeout=0):
    try:
      ret=bc_submit_captcha(self.__key, image)
      return {"captcha":image, "text":ret}
    except:
      return None


def bc_split(data):
	ret = {}
	lines = data.splitlines()
	for line in lines:
		space_idx = line.find(' ')
		if space_idx < 0:
			continue
		name = line[:space_idx]
		value = line[space_idx+1:]
		ret[name] = value
	return ret

def bc_post_data(url, data):
	p = urllib.urlencode(data)
	f = urllib.urlopen(url, p)
	con = f.read()
	f.close()
	return bc_split(con)

def bc_submit_captcha(key, img):
	task_id = -1
	con = base64.b64encode(img)
	ret = bc_post_data("http://bypasscaptcha.com/upload.php", \
			{ "key": key, "file": con, "submit": "Submit", "gen_task_id": 1, "base64_code": 1})
	v = {}
	if "TaskId" in ret:
		v['task_id'] = ret['TaskId']
	else:
		raise Exception("Decode failed")
	v['value'] = ret['Value']
	v['key'] = key
	return v

def bc_submit_feedback(v, is_input_correct):
	if is_input_correct:
		is_input_correct = 1
	else:
		is_input_correct = 0
	bc_post_data("http://bypasscaptcha.com/check_value.php", \
			{ "key": v['key'], 'task_id': v['task_id'], 'cv': is_input_correct, 'submit': 'Submit' })

def bc_get_left(key):
	ret = bc_post_data("http://bypasscaptcha.com/ex_left.php",\
			{ "key": key})
	return ret['Left']

