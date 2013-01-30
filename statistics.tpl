<!doctype html>
<html>
<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
	<title>jshint扫描结果</title>
	<style>%(style)s</style>
</head>
<body>
	<section>
		%(title)s
		<p>scanned %(files_count)s files in %(time_used).2f seconds, passed <b class="green">%(passed_count)d</b>, failed <b class="red">%(failed_count)d</b>, pass rate <b class="green">%(pass_rate).1f%%</b></p>
		<p>jshint options:</p>
		<code>%(jshint_options)s</code>
		<p>details:</p>
	</section>
	<section id="file_list">
		<table id="file_list_table" border=1>
			<thead>
				<td>path</td>
				<td width=60>result</td>
				<td width=60>error count</td>
				<td width=60>warning count</td>
			<thead>
				<tbody>%(table_data)s</tbody>
		</table>
	</section>
	<section id="error_list">
	<ul>%(output_data)s</ul>
	</section>
</body>
</html>

