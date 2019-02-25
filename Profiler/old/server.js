/* 
 * Profiler -> server.js
 * ----------------------------------------------------------------------------------------------------
 * 
 * Author: Ronnie Smith <ronnie.smith@ed.ac.uk / ras35@hw.ac.uk>
 * Version: 1.0
 * Date: 25th February 2019
 * 
 */

/* 
 * Defintions and Global Variables
 * ----------------------------------------------------------------------------------------------------
 */

// Packages
var express = require('express');
var path = require('path');
const router = express.Router()

// MongoDB
var dbName = "Profiler";
var mongo = require('mongodb');
var mongoClient = require('mongodb').MongoClient;
var db = require('mongodb').Db;
var con_url = "mongodb://localhost:27017/" + dbName;

/* 
 * Express
 * ----------------------------------------------------------------------------------------------------
 */

var app = express();
var http = require('http').Server(app);
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', function(req, res){
  res.sendFile(__dirname + '/index.html');
});

var IPSController = require('./routes/main');
app.use('/main', IPSController);

http.listen(3001, function(){
  console.log('listening on *:3001');
});

module.exports = app;

/* 
 * DB Manipulation Functions  
 * ----------------------------------------------------------------------------------------------------
 */

function addPerson(data){

    mongoClient.connect(con_url, function(err, db){
        if(err) throw err;
        db.collection("People").insert(data, function(err, res) {
            if (err) throw err;
            console.log("Added 1 person to People collection.");
            db.close();
        });
    });

}

function retrievePerson(data){

    mongoClient.connect(con_url, function(err, db){
        if(err) throw err;
        db.collection("People").find().toArray(function(err, docs) {
            console.log(JSON.stringify(docs));
            db.close();
        });
    });

}