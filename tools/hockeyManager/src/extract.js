
function delay(time) {
  return new Promise(resolve => setTimeout(resolve, time));
}

/* Player Detail */
function getPlayerStats(id,player_stats) {
	gtag('config', 'UA-298737-1', {
	  'page_title' : 'Player detail',
	  'page_path': '/player-detail/' + id
	});
	var data = {
		'id' : id
		};
	var randomnumber = Math.floor(Math.random()*1000000000);	
	$.post(app_site_start + 'ajaxrequest/get-player-detail', data , function (result) { 
			if (result) { 
					player_stats.push(result.replace('"','[[').replace('\n','').replace(',',' '));
			}else{
					player_stats.push('Error');
			}
		});
}	

var NBENTRIES=7;

function get_player_list(list){
	players = list.getElementsByClassName('tr row')
	data = []
	for(let i = 0; i < players.length; i++){
		var player = players[i]
		
		
		var player_id = player.getAttribute('attr')
		cols = players[i].getElementsByClassName('td')
		var player_position = cols[0].innerText
		var player_name=cols[1].innerText
		var player_team=cols[2].children[0].getAttribute('src')
		var player_value=cols[3].innerText
		var player_nat=cols[4].children[0].getAttribute('src')
		// IF this is change, need to change constante above NBENTRIES
		var player_stats = [player_id,player_position,player_name,player_team,player_value,player_nat]
		
		// open player detail
		getPlayerStats(player_id,player_stats);	
		
		
		data.push(
			player_stats
		)
	}
	
	
	return data
}

 function arrayToCsv(data){
  return data.map(row =>
    row
    .map(String)  // convert every value to String
    .map(v => v.replaceAll('"', '""'))  // escape double quotes
    .map(v => `"${v}"`)  // quote it
    .join(',')  // comma-separated
  ).join('\r\n');  // rows starting on new lines
}

/** Download contents as a file
 * Source: https://stackoverflow.com/questions/14964035/how-to-export-javascript-array-info-to-csv-on-client-side
 */
 function downloadBlob(content, filename, contentType) {
  // Create a blob
  var blob = new Blob([content], { type: contentType });
  var url = URL.createObjectURL(blob);

  // Create a link to download it
  var pom = document.createElement('a');
  pom.href = url;
  pom.setAttribute('download', filename);
  pom.click();
}

function get_and_download_players(list_name,csv_name){
	var myPlayersList = document.getElementsByClassName(list_name)[0]

	var myPlayersData =  get_player_list(myPlayersList)
	
	function do_when_finished(remaining_loop){
	  var isOk = true
	  for(let i = 0; i < myPlayersData.length; i++){
		if(myPlayersData[i].length < NBENTRIES){
			isOk=false
		}
	  }
	  if(isOk || remaining_loop<0){
		var myPlayersCSV =  arrayToCsv(myPlayersData)

		downloadBlob(myPlayersCSV,csv_name,'text/csv;charset=utf-8;')
	  }else{
	     setTimeout(() => {do_when_finished(remaining_loop-1) }, 1000);
	  }
	  
	}
	
	do_when_finished(500)
	
	
	
}


get_and_download_players('myteam','my_players.csv')


get_and_download_players('freeagents','other_players.csv')


