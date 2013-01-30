#!/usr/bin/python
#-*- coding: utf-8 -*-
import sys
import os
import logging
import subprocess
import re
import getopt
import time
from os.path import normpath,join

reload(sys)
sys.setdefaultencoding("utf-8")

TERM_COLOR_SUPPORT = False
log = None # 日志对象
exit_code = 0 # 程序退出码
time_used = 0 # 使用的时间统计
files_count = 0 # 扫描的文件数目统计
lint_failed_count = 0 # lint失败的文件个数
jshint_opts = None # jshint选项
result_data = [] # 记录结果，依次为路径，是否通过，错误数，警告数，错误信息，id序号

try:
	from colorama import init,Fore
	init()
	TERM_COLOR_SUPPORT = True
except:
	pass

def scanJsFileInTree(root):
	"""Scan directory for Javascript file"""
	return scanTree(root,re.compile(r'^.+\.js$'))

def scanTree(root, path_filter=None, scan_hidden=False):
	"""Scan directory for files"""
	for dirpath,dirnames,filenames in os.walk(root):
		for dirname in dirnames[:]:
			if not scan_hidden and dirname.startswith('.'):
				dirnames.remove(dirname)#dont enter that dir
		
		for filename in filenames:
			if not scan_hidden and filename.startswith('.'):
				continue#dont list that file
		
			fullpath = os.path.join(dirpath, filename)
		
			if path_filter and not path_filter.match(fullpath):
				continue#dont list that file 2
		
			yield os.path.normpath(fullpath)

def initLogger(name):
	"""Initialize logger"""
	global log
	log = logging.getLogger("jshint")
	console = logging.FileHandler(name)
	console.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
	log.setLevel(logging.DEBUG)
	log.addHandler(console)

def print_wz_color(msg, status, color):
	"""Print one line message on stdoout with ansi color"""
	if TERM_COLOR_SUPPORT:
		if color == "red":
			status = Fore.RED + "%s" % status + Fore.RESET
		elif color == "green":
			status = Fore.GREEN + "%s" % status + Fore.RESET
	print "%s %s" % (msg, status)

def jshint_dir_run(js_dir_path, opt_file, reporter, quiet):
	"""Run jshint in directory"""
	for jsfile in scanJsFileInTree(js_dir_path):
		jshint_run(jsfile, opt_file, reporter, quiet)

def jshint_run(js_file, lint_opt, reporter, quiet=False):
	"""Run jshint"""
	global jshint_opts, files_count, lint_failed_count, time_used, exit_code
	global result_data
	result = []
	if not jshint_opts:
		jshint_opts = open(lint_opt,"r").read()
	start_time = time.time()
	js_file = os.path.abspath(js_file)
	result.append(js_file) # 路径
	cmd = "jshint %s --config %s --reporter %s" % (js_file, lint_opt, reporter)
	msg = "%s" % js_file
	if log:
		log.debug(msg)
	files_count = files_count + 1
	process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	process_output = process.communicate()[0]
	process_retcode = process.returncode
	end_time = time.time()
	time_used = time_used + end_time - start_time
	if log and process_output:
		log.debug(process_output)
	success = "success"
	fail = "fail"
	status = success
	color = "green"
	err_count = 0
	warn_count = 0
	if process_retcode != 0:
		status = fail
		color = "red"
	if log:
		log.debug("%s" % status)
	result.append(status) # 是否通过
	if status == fail:
		exit_code = 3
		lint_failed_count = lint_failed_count + 1
		err_count_match = re.search('(\d+)Error', process_output)
		warn_count_match = re.search('(\d+)Warning', process_output)
		if err_count_match:
			err_count = err_count_match.groups()[0]
		if warn_count_match:
			warn_count = warn_count_match.groups()[0]
		if err_count_match or warn_count_match:
			#status = "%s %s errors %s warnings" % (status, err_count, warn_count)
			pass
	result.append(err_count) # 错误数量
	result.append(warn_count) # 警告数量
	result.append(process_output) # 检查结果
	result.append(files_count) # 唯一id
	result_data.append(result)
	if not quiet:
		print_wz_color(msg, status, color)

#询问目录
def askDir(**kwargs):
	import Tkinter, tkFileDialog
	root = Tkinter.Tk()
	root.withdraw()
	return tkFileDialog.askdirectory(parent=root,**kwargs)

def usage():
	"""Print the help"""
	print "Usage:\n"\
		+ "python %s [options]\n\n" % os.path.basename(sys.argv[0])\
		+ "options:\n"\
		+ "--help               print this message\n"\
		+ "--quiet              prevent logging message to stdout\n"\
		+ "--statistics         show statistics in a browser\n"\
		+ "--select             select a folder manaually\n"\
		+ "--log    [filename]  generate log\n"\
		+ "--path   [path]      run jslint on specified directory or file\n"\

def showStatistics():
	tpl = open("statistics.tpl","r").read()
	style = open("statistics.style","r").read()
	title = "<h2 class='red'>Fail</h2>"
	if lint_failed_count == 0:
		title = "<h2 class='green'>Success</h2>"
	statistics = tpl % {"files_count": files_count,
			"style": style,
			"time_used": time_used,
			"jshint_options": jshint_opts,
			"title": title,
			"passed_count": files_count - lint_failed_count,
			"failed_count": lint_failed_count,
			"pass_rate": (1 - float(lint_failed_count) / files_count) * 100,
			"table_data": "".join(["<tr><td><a id=\"table_seq_"
					+ str(item[5]) # id
					+ "\" href=\"#result_seq_"
					+ str(item[5]) # id
					+ "\">"
					+ item[0].decode("gbk").encode("utf-8") # path
					+ "</a>"
					+ "</td><td class=\"center" + (" red" if item[1] == "fail" else " green") + "\">"
					+ str(item[1]) # reult
					+ "</td><td class=\"center\">"
					+ str(item[2]) # err count
					+ "</td><td class=\"center\">"
					+ str(item[3]) # warn count
					+ "</tr>" for item in result_data]),
			"output_data": "".join(["<li><a id=\"result_seq_"
					+ str(item[5]) # id
					+ "\" href=\"#table_seq_"
					+ str(item[5]) # id
					+ "\">"
					+ item[0].decode("gbk").encode("utf-8") # path
					+ "</a><pre>" 
					+ (item[4] if item[4] else "") #output
					+ "</pre></li>" for item in result_data])}
	f = open("statistics.html","w")
	f.write(statistics)
	f.close()
	import webbrowser
	webbrowser.open(f.name)

def main(argv):
	"""Main entry"""
	cwd = os.getcwd()
	reporter = normpath(join(cwd,"reporter"))
	opt_file = normpath(join(cwd,"jshintrc"))
	quiet = None
	spath = None
	statistics = None
	select = None
	try:
		opts,args = getopt.getopt(argv, "", ["help", "quiet", "statistics", "select", "log=", "path="])
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)
	for opt, v in opts:
		if opt == "--help":
			usage()
			sys.exit()
		elif opt == "--quiet":
			quiet = True
		elif opt == "--statistics":
			statistics = True
		elif opt == "--select":
			select = True
		elif opt == "--log":
			initLogger(v)
		elif opt == "--path":
			spath = v

	if spath:
		if not os.path.exists(spath):
			print "path \"%s\" not exists" % spath
			sys.exit(2)
		else:
			if os.path.isdir(spath):
				jshint_dir_run(spath, opt_file, reporter, quiet)
			elif os.path.isfile(spath):
				jshint_run(spath, opt_file, reporter, quiet)
			else:
				print "invalid path \"%s\"" % spath
				sys.exit(2)
	elif select:
		selected_dir = askDir(title=u"选择目录")
		jshint_dir_run(os.path.normpath(selected_dir).encode("gbk"), opt_file, reporter, quiet)
	else:
		usage()
	
	if statistics:
		showStatistics()

	sys.exit(exit_code)

if __name__ == "__main__":
	main(sys.argv[1:])

