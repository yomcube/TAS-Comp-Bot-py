var score = [];
var scoreMsgID = ["",""]; // [channel_id, message_id]
var task = 1;
var setLength = 5;

const miscfuncs = require("./miscfuncs.js");
const save = require("./save.js");

module.exports = {

  // k=place, n=participants
  // points = 15x^6 + 10x^4 + 5x^2 + 14x + 6
  alg:function(k,n) {
    x = (n-k+1) / n;
    points = 15*x*x*x*x*x*x + 10*x*x*x*x + 5*x*x + 14*x + 6;
    return parseFloat(points.toFixed(1));
  },



  // a = ["1. Name time miscinfo"]
  // return = [int(place), "Name", float(points)]
  resultsToScore:function(a) {

    var score = [];
    var name, place, points, coop, participants;

    // remove DQs and empty lines
    for (var i = a.length - 1; i>=0; i--){
      if (a[i] == '' || a[i].toUpperCase().substr(0,2) == "DQ" || a[i].toUpperCase().substr(0,4) == "HTTP"){
        a.splice(i,1);
      }
    }

    participants = a.length;

    for (var i = 0; i < participants; i++){

      // assumes there is a space between place and name
      name = a[i].split(" ")[1];

      place = parseInt(a[i]);

      points = this.alg(place, participants);

      score.push([place, name, points]);

      // co-op results
      coop = a[i].indexOf("&");

      if (coop != -1){

        name = a[i].substring(coop+1, a[i].length).trim();
        name = name.split(" ")[0];
        score.push([place, name, points]);
      }
    }

    return score;
  },



  // GETTERS and SETTERS
  getScore:function(){
    return this.score;
  },
  setScore:function(a){
    this.score = [];
    while (a.length > 0){
      this.score.push(a.shift());
    }
  },
  getScoreMsg:function(){
    return this.scoreMsgID;
  },
  setScoreMsg:function(channel, msg){
    this.scoreMsgID = [channel, msg];
  },
  getTask:function(){
    return this.task;
  },
  setTask:function(num){
    if (!isNaN(parseInt(num))){
      this.task = parseInt(num);
    }
  },
  getSetLength:function(){
    return this.setLength;
  },
  setSetLength:function(num){
    if (!isNaN(parseInt(num))){
      this.setLength = parseInt(num);
    }
  },




  // scores = [int(place), "Name", float(points)]
  addScores:function(a, b){

    if (a === undefined || a.length == 0 || a[0].length == 0){return b;}
    if (b === undefined || b.length == 0 || b[0].length == 0){return a;}

    var NewScore = [];
    var name = "";
    var points = 0.0;

    for (var i=0; i<a.length; i++){

      name = a[i][1];
      points = parseFloat(a[i][2]);

      // check if the player appears in both
      for (var j=0; j<b.length; j++){

        if (name.toUpperCase() == b[j][1].toUpperCase()){
          // remove the duplicate from b as to not check them again
          points += parseFloat(b.splice(j,1)[0][2]);
          points = parseFloat(points.toFixed(1));
          break;
        }
      }

      NewScore.push([0, name, points]);
    }

    // any remaining players only in b
    for (var i=0; i<b.length; i++){
      NewScore.push([0, b[i][1], parseFloat(b[i][2].toFixed(1))]);
    }

    return NewScore;

  },



  // returns score with proper placement
  sortScore:function(a){

    if (a === undefined || a.length == 0 || a[0].length == 0){return [[]];}
    if (a.length == 1){return [[1, a[0][1], a[0][2]]];}

    // sort by descending points
    a = a.sort((a,b) => b[2] - a[2]);

    a[0][0] = 1;

    for (var i=1; i<a.length; i++){

      // same points as previous => same place as previous
      if (a[i][2] == a[i-1][2]){

        a[i][0] = a[i-1][0];

      } else {

        a[i][0] = i+1;
      }

    }

    return a;

  },



  scoreToMessage:function(a, task, set, useHeader){

    if (a === undefined || a.length == 0  || a[0].length == 0){return "No Results";}

    var msg = "**";

    if (useHeader === undefined){useHeader = true;}

    if (useHeader){

      if (set === undefined){

        if (task === undefined){task = 1;}

        set = ~~((parseInt(task) - 1) / this.setLength) + 1;
      }

      msg += "__Set " + set.toString() + " Score ";
      msg += "After Task " + task.toString() + "__\n\n";
    }

    var stopBold = true;
    var place = 0;
    var name = "";
    var points = 0.0;

    for (var i=0; i<a.length; i++){

      place = a[i][0];
      name = a[i][1];
      points = a[i][2];

      // bold top 3
      if (place>3 && stopBold){
        msg += "**";
        stopBold = false;
      }

      msg += place.toString();

      // Checks last character of place => 1st, 2nd, 3rd, 4th...
      // Checks 2nd last character for 11th, 12th, 13th, 111th...
      var last = place.toString().split('')[place.toString().length-1];
      var secondLast = place.toString().split('')[place.toString().length-2];
      switch (last) {
        case "1":
          if (secondLast!="1"){
            msg += "st";
            break;
          }

        case "2":
          if (secondLast!="1"){
            msg += "nd";
            break;
          }

        case "3":
          if (secondLast!="1"){
            msg += "rd";
            break;
          }

        default:
          msg += "th"
          break;
      }

      msg += ". " + name + ": " + points.toString();

      if (points.toString().substr(-2,1) != "."){msg += ".0";}

      msg += "\n";

    }

    if (stopBold){
      msg += "**";
    }

    return msg;

  },



  updateScore:function(resultsMessage){
    var msg = "";
    try {

      // reset scores at the start of a new set
      if ((this.getTask()) % this.getSetLength() == 0){this.setScore([]);}
      this.setTask(this.getTask() + 1);

      var pastScore = this.getScore();

      var results_s = resultsMessage.split("\n")
      results_s.splice(0,2); // remove title and empty line

    	var results = this.resultsToScore(results_s);

    	var newScore = this.addScores(pastScore, results);
    	newScore = this.sortScore(newScore);

    	this.setScore(newScore);

    	msg = this.scoreToMessage(this.getScore(), this.getTask());

    } catch (e) {

      msg = "Could not process results```"+e.toString()+"```";

    } finally {

      return msg;
    }
  },



  changeName:function(oldName, newName){

    var score = this.getScore();
    if (score === undefined || score.length == 0  || score[0].length == 0){
      return "No score found.";
    }

    for (var i=0; i<score.length; i++){

      if (score[i][1].toUpperCase() == oldName.toUpperCase()){
        score[i][1] = newName;
        return "Changed ``"+oldName+"`` to ``"+newName+"``";
      }

    }

    return "Name ``"+oldName+"`` not found in score.";

  },



  changePoints:function(name, points){

    var score = this.getScore();
    if (score === undefined || score.length == 0  || score[0].length == 0){
      return "No score found.";
    }

    var num = parseFloat(points);
    var oldpts;

    if (isNaN(num)){
      return "``<points>`` must be a float.";
    }

    for (var i=0; i<score.length; i++){

      if (score[i][1].toUpperCase() == name.toUpperCase()){
        oldpts = score[i][2].toFixed(1);
        score[i][2] = parseFloat(num.toFixed(1));
        return "Changed ``"+name+"``'s points from ``"+oldpts.toString()+"`` to ``"+num.toFixed(1)+"``.";
      }

    }

    return "Name ``"+name+"`` not found in score.";

  },



  // a = ["1. Name: Points"]  // assumes proper input
  // return = [[1, name, points]]
  scoreMessageToScore:function(a){

    var score = []
    var place = 0;
    var name = "";
    var points = 0.0;

    for (var i = 0; i<a.length; i++){

      place = parseInt(a[i].split(" ")[0]);
      name = a[i].split(" ")[1];
      points = parseFloat(a[i].split(" ")[2]);

      //remove colon "1st. Name: Score"
      if (name.substring(name.length-1) == ":"){
        name = name.substring(0, name.length-1);
      }

      score.push([place, name, points]);

    }

    return score;

  },



  remove:function(name){

    var score = this.getScore();
    if (score === undefined || score.length == 0  || score[0].length == 0){
      return "No score found.";
    }

    for (var i=0; i<score.length; i++){

      if (name.toUpperCase() == score[i][1].toUpperCase()){

        var line = score.splice(i, 1);
        score = this.sortScore(score);
        this.setScore(score);

        return "Removed: ``"+line[0][0].toString()+". "+line[0][1]+": "+line[0][2]+"``.";

      }
    }

    return "Name ``"+name+"`` not found in score.";

  },



  combine:function(name1, name2){

    name1 = name1.toUpperCase();
    name2 = name2.toUpperCase();

    if (name1 == name2){return "Cannot combine the same name.";}

    var score = this.getScore();
    if (score === undefined || score.length == 0  || score[0].length == 0){
      return "No score found.";
    }

    for (var i=0; i<score.length; i++){

      if (score[i][1].toUpperCase() == name1){

        for (var j=0; j<score.length; j++){

          if (score[j][1].toUpperCase() == name2){

            score[i][2] = (parseFloat(score[i][2]) + parseFloat(score.splice(j,1)[0][2])).toFixed(1);
            score = this.sortScore(score);
            this.setScore(score);
            return "Combined ``"+name1+"`` & ``"+name2+"``.";

          }
        }

        return "Name ``"+name2+"`` not found in score.";

      }
    }

    return "Name ``"+name1+"`` not found in score.";

  },



  // perform a request given an action and the arguments
  processRequest:function(user, action, args){

    console.log(user.username + " " + action); // record who calls commands
    var msg = "";

    switch (action) {
      case "PRINT":

        // optional task
        var task = 0;
        if (args.length > 0){task = parseInt(args.shift());}

        // optional set
        var set = ~~((task - 1)/ this.setLength ) + 1;
        if (args.length > 0){set = parseInt(args.shift());}

        msg = this.scoreToMessage(this.getScore(), task, set, task!=0);
        break;

      case "FIND":
        if (args.length == 0){
          msg = "Not enough arguments: ``<name>``";
        } else {

          // shorthand for using their username
          if (args[0].toUpperCase() == "ME"){
            args[0] = user.username.replace(/ /g, '');
          }

          var score = this.getScore();
          var found = false;
          for (var i=0; i<score.length; i++){
            if (score[i][1].toUpperCase() == args[0].toUpperCase()){
              var a = [score[i][0], score[i][1], score[i][2]];
              msg = "``"+this.scoreToMessage([a],0,0,false)+"``";
              while (msg.includes("*")){msg = msg.replace("*","");}
              found = true;
            }
          }

          if (!found){msg = "Name ``"+args[0].toUpperCase()+"`` not found in score.";}

        }
        break;

      case "SET":
        var results = this.scoreMessageToScore(args);
        results = this.sortScore(results);
        this.setScore(results);
        msg = "Score set."
        break;

      case "CLEAR":
        this.setScore([]);
        msg = "Score cleared.";
        break;

      case "CHANGENAME":
        if (args.length < 2){
          msg = "Not enough arguments: ``<oldName>`` ``<newName>``.";

        } else {
          msg = this.changeName(args[0], args[1]);
        }
        break;

      case "CHANGEPOINTS":
      if (args.length < 2){
        msg = "Not enough arguments: ``<name>`` ``<points>``.";

      } else {
        msg = this.changePoints(args[0], args[1]);
      }
      break;

      case "COMBINE":
        if (args.length < 2){
          msg = "Not enough arguments: ``<name1>`` ``<name2>``.";

        } else {
          msg = this.combine(args[0], args[1]);
        }
        break;

      case "ADD":
        if (isNaN(parseFloat(args[1]))){args[1]=0.0;} // default points to 0

        var newScore = [[0, args[0], parseFloat(args[1])]]
        newScore = this.addScores(this.getScore(), newScore);

        newScore = this.sortScore(newScore);
        this.setScore(newScore);

        msg = "Added ``"+args[0]+": "+args[1]+"``.";
        break;

      case "REMOVE":
        if (args.length == 0){
          msg = "Not enough arguments: ``<name>``.";

        } else {
          msg = this.remove(args[0]);
        }
        break;

      case "CHANGESETLENGTH":
        if (isNaN(parseInt(args[0]))){
          msg = "Set length must be an integer.";
        } else {
          this.setLength = parseInt(args[0]);
          msg = "Score will reset every " + parseInt(args[0]).toString() + " tasks.";
        }
        break;

      case "SETMESSAGE":
        if (args.length < 2) {
          msg = "Not enough arguments: ``<channel_ID> <message_ID>``.";
        } else {
          this.setScoreMsg(args[0], args[1]);
          msg = "Message set. " + this.getScoreMsg()[0] + " " + this.getScoreMsg()[1];
        }
        break;

      case "CHANGETASK":
        if (args.length == 0) {
          msg = "Not enough arguments: ``<task#>``.";
        } else {
          if (isNaN(parseInt(args[0]))){
            msg = "Task must be a number."
          } else {
            msg = "Task number set to "+parseInt(args[0]).toString()+".";
            this.setTask(parseInt(args[0]));
          }
        }
        break;

      case "CALCULATE":
        if (isNaN(parseInt(args[0]))){
          msg = "Score length must be an integer.";
        } else {

          // get the score portion
          var score = [];
          var scoreLength = args.shift();
          for (var i=0; i<scoreLength; i++){
            score.push(args.shift());
          }
          score = this.scoreMessageToScore(score);

          // any remaining results
          var results = [];
          var remaining = args.length;
          for (var i=0; i<remaining; i++){
            results.push(args.shift());
          }
          results = this.resultsToScore(results);

          var newScore = this.addScores(score, results);
          newScore = this.sortScore(newScore)
          msg = this.scoreToMessage(newScore,0,0,false);

        }
        break;

      default:
        if (action!="HELP"){msg = "Failed request, action: ``"+action+"`` not recognized. ";}
        msg += "Action must be ";
        ["PRINT","FIND","SET","CLEAR","CHANGENAME","CHANGEPOINTS","COMBINE","ADD","REMOVE","CHANGESETLENGTH","CHANGETASK","SETMESSAGE"].forEach(function(a){
          msg += "``"+a+"``, ";
        });
        msg+="``CALCULATE``.";
        break;

    }

    return msg;

  },



  // parses input from a user and responds accordingly
  processCommand:function(bot, msg, args){


    var action = "";
    var message = "";

    if (msg.content.split(" ").length == 1){
      action = "HELP";
    } else {
      action = msg.content.split("\n")[0].split(" ")[1].toUpperCase();
    }

    // allow people to calculate scores and find themselves
    if (["FIND","CALCULATE"].includes(action) || miscfuncs.hasCmdAccess(msg)){

      var params = [];

      if (action == "SET" || action == "CALCULATE"){
        params = msg.content.split("\n");
        params = params.splice(1, params.length - 1)
      } else {
        params = msg.content.split(" ");
        params = params.splice(2, params.length - 1)
      }

      // check that the message is a valid message from the bot
      if (action == "SETMESSAGE"){
        if (params.length >= 2){

          bot.getMessage(params[0], params[1]).then((msg) => {

            if (msg.author.id != BOT_ACCOUNT){
              return "Invalid user. Message must be sent by me.";
            }

          }).catch((error) => {
            return "Invalid channel or message. Could not find message.";
          });

        }
      }

      message = this.processRequest(msg.author, action, params);

      // directly edit the message in #SCORE
      if (["CHANGENAME","CHANGEPOINTS","COMBINE","ADD","REMOVE","CLEAR","SET","CHANGETASK","CHANGESETLENGTH","SETMESSAGE"].includes(action)){
        this.saveVars();
        if (this.getScoreMsg()[0] == ""){
          message += " No message found to edit.";
        } else {
          bot.editMessage(this.getScoreMsg()[0],this.getScoreMsg()[1],this.scoreToMessage(this.getScore(), this.getTask()));
        }
      }

    // someone who doesn't have access, didnt use find or calculate
    } else {
      return "Missing permissions. Try ``$score find`` or ``$score calculate``"
    }

    return message;
  },


  // loads variables from save and verifies the message
  retrieveScore:function(bot){
    this.loadVars();
    var channel_id = this.getScoreMsg()[0];
    var message_id = this.getScoreMsg()[1];
    bot.getMessage(channel_id, message_id).catch((error) => {
      this.setScoreMsg("","");
      console.log("WARNING: Invalid score message");
    });
  },

  saveVars:function(){
    var vars = {
      score: this.getScore(),
      channel_id: this.getScoreMsg()[0],
      message_id: this.getScoreMsg()[1],
      task: this.getTask(),
      set_length: this.getSetLength()
    }
    save.saveObject("score.json", vars);
  },

  loadVars:function(){
    var vars = save.readObject("score.json");
    this.setScore(vars.score);
    this.setScoreMsg(vars.channel_id, vars.message_id);
    this.setTask(vars.task);
    this.setSetLength(vars.set_Length);
  },

  autoUpdateScore:async function(bot, msg){
    // TODO: Move function outside of main such that only this function call is required from bot.onMessageCreate
    // Potentially handle setting the results and score channels
    // Use either ID or #mention (message.channelMentions[0])
    if (msg.channel.id == ResultsChannel && msg.content.split("\n")[0].toUpperCase().indexOf("DQ") == -1){
      var message = score.updateScore(msg.content);
      let msg = await bot.createMessage(ScoreChannel, message);
      scoreMsgID = [msg.channel.id, msg.id]
      saveVars();
    }
  },

  help:function(command){
    var msg = "";
    msg += "Usage: ``$score <action> <args...>``\n";
    msg += "\nAnyone can use the following commands:";
    msg += "```$score find <username or 'me'>```";
    msg += "```$score calculate *<length of previous score> *<previous scores...> *<results...>```";
    msg += "\nUsers with access may use the following commands:";
    msg += "```$score print [task_number] [set_number]```";
    msg += "```$score set *<scores...>```";
    msg += "```$score clear```";
    msg += "```$score changename <old_name> <new_name>```";
    msg += "```$score changepoints <name> <new_points>```";
    msg += "```$score combine <name1> <name2>```";
    msg += "```$score add <name> [points]```";
    msg += "```$score remove <name>```";
    msg += "```$score changesetlength <set_length>```";
    msg += "```$score changetask <task_number>```";
    msg += "```$score setmessage <channel_id> <message_id>```";
    msg += "\n``*`` Denotes arguments that must appear on new lines\n";
    msg += "``[]`` Denotes optional arguments\n";
    msg += "``...`` Denotes that multiple arguments may be entered\n";
    msg += "\nFor more information on specific actions, contact Xander"; // actions, use ``$score help <action>`` or contact Xander
    return msg;
  }

};
