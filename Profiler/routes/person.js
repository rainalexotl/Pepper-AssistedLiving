const express = require('express')
const router = express.Router()
const mongoose = require('mongoose')

const Person = require('../models/person')

const handleError = error => {
  return console.log(error)
}

// Test
router.get('/test', function (req, res, next) {
  res.header('CALL', `/api/person/test`)
  res.status(201)
  res.json({
    success: true,
    message: 'Hello, World',
  })
})

/* 
 * Method: POST
 * Behav.: Adds a new person
 * 
 * Params: forename (req.body.forename)
 *         surname  (req.body.surname)
 */
router.post('/add/person', function (req, res, next) {
  const p = new Person()

  Person.findOne( { forename: req.body.forename }, function (err, person) {
    if (err) {
      res.status(400)
      return res.json({
        success: false,
        message: err.message
      })
    }
    if (!person) {
      p.forename = req.body.forename
      p.surname = req.body.surname
    
      p.save(function (err, newPerson) {
        if (err) {
          res.status(400)
          return res.json({
            success: false,
            message: err.message
          })
        }
    
        res.header('CALL', `/api/person/add/Person`)
        res.status(201)
        res.json({
          success: true,
          message: 'New Person Added',
          person: newPerson.toJSON()
        })
      })
    }
    else{
      res.status(400)
      return res.json({
        success: false,
        message: "A person already exists with this name."
      })
    }
  })
})

/* 
 * Method: POST
 * Behav.: Adds a new like for an existing person
 * 
 * Params: forename    (req.body.forename)
 *         likeDislike (req.body.likeDislike)
 *         thing       (req.body.thing)
 */
router.post('/add/likeDislike', function (req, res, next) {

  Person.findOne({ forename: req.body.forename }, function (err, person){

    if(req.body.likeDislike && req.body.thing){
      var newLikeDislike = { likeDislike: req.body.likeDislike, thing: req.body.thing}
      person.likesDislikes.push(newLikeDislike)

      person.save(function (err, p) {
        if (err) {
          res.status(400)
          return res.json({
            success: false,
            message: err.message
          })
        }
    
        res.header('CALL', `/api/person/add/likeDislike`)
        res.status(201)
        res.json({
          success: true,
          message: 'New Like/Dislike Added',
          person: p.toJSON()
        })
      })
    }
    else{
      res.status(400)
      return res.json({
        success: false,
        message: "Params: forename (req.body.forename), likeDislike (req.body.likeDislike), thing (req.body.thing)"
      })
    }
  })
})

/* 
 * Method: POST
 * Behav.: Gets all likes for a given user
 * 
 * Params: forename (req.body.forename)
 */
router.post('/likes', function (req, res, next) {

  Person.findOne({ forename: req.body.forename }, function (err, person){

    Person.aggregate([{ $match: { "forename": req.body.forename } }, { $project: { likesDislikes: 1 } }, { $unwind: '$likesDislikes' }, { $match: { "likesDislikes.likeDislike": true } }]).exec((err, likes) => {
      if(err) {
        res.status(400)
        return res.json({
          success: false,
          message: err.message
        })
      }
  
      var arrayLikes = []
      for(i = 0; i < likes.length; i++){
        arrayLikes.push({"thing":likes[i].likesDislikes.thing})
      }

      res.header('CALL', '/api/person/likes')
      res.status(201)
      res.json({
        success: true,
        message: 'User Likes Retrieved',
        likes: arrayLikes
      }) 
    })
  })
})

/* 
 * Method: POST
 * Behav.: Gets all background information for a given user
 * 
 * Params: forename (req.body.forename)
 */
router.post('/background', function (req, res, next) {

  Person.findOne({ forename: req.body.forename }, function (err, person){

    Person.aggregate([{ $project: { background: 1 } }, { $unwind: '$background' } ]).exec((err, background) => {
      if(err) {
        res.status(400)
        return res.json({
          success: false,
          message: err.message
        })
      }

      res.header('CALL', '/api/person/background')
      res.status(201)
      res.json({
        success: true,
        message: 'User Background Retrieved',
        background: background[0].background
      }) 
    })
  })
})

/* 
 * Method: POST
 * Behav.: Gets common likes between two users
 * 
 * Params: forename of first person  (req.body.forename_1)
 *         forename of second person (req.body.forename_1)
 */
router.post('/commonlikes', function (req, res, next) {

  if(req.body.type == "general"){
    Person.find({ }, function (err, people){

      res.header('CALL', '/api/person/commonlikes')
      res.status(201)
      res.json({
        success: true,
        message: 'User Likes Retrieved (Thing)',
        allPeople: people
      })

    })
  }
  else if(req.body.type == "specific_friend") {
    Person.findOne({ forename: req.body.forename_1 }, function (err, person){

      Person.aggregate([{ $match: { "forename": req.body.forename_1 } }, { $project: { likesDislikes: 1 } }, { $unwind: '$likesDislikes' }, { $match: { "likesDislikes.likeDislike": true } }]).exec((err, likesP1) => {
        if(err) {
          res.status(400)
          return res.json({
            success: false,
            message: err.message
          })
        }
  
        var arrayLikesP1 = []
        for(i = 0; i < likesP1.length; i++){
          arrayLikesP1.push({"thing":likesP1[i].likesDislikes.thing})
        }
  
        Person.findOne({ forename: req.body.forename_2 }, function (err, person){
  
          Person.aggregate([{ $match: { "forename": req.body.forename_2 } }, { $project: { likesDislikes: 1 } }, { $unwind: '$likesDislikes' }, { $match: { "likesDislikes.likeDislike": true } }]).exec((err, likesP2) => {
            if(err) {
              res.status(400)
              return res.json({
                success: false,
                message: err.message
              })
            }
        
            var arrayLikesP2 = []
            for(i = 0; i < likesP2.length; i++){
              arrayLikesP2.push({"thing":likesP2[i].likesDislikes.thing})
            }
  
            console.log(arrayLikesP1)
            console.log(arrayLikesP2)
  
            var commonLikes = []
  
            for(i = 0; i < arrayLikesP1.length; i++){
              for(j = 0; j < arrayLikesP2.length; j++){
                if(arrayLikesP1[i].thing == arrayLikesP2[j].thing){
                  commonLikes.push(arrayLikesP1[i].thing)
                }
              }
            }
  
            console.log(commonLikes)
  
            res.header('CALL', '/api/person/commonlikes')
            res.status(201)
            res.json({
              success: true,
              message: 'User Likes Retrieved',
              commonLikes: commonLikes
            })
          })
        })
      })
    })
  }
})

/* 
 * Method: POST
 * Behav.: Shuts down the profile system.
 * 
 * Params: command ("SHUTDOWN")
 */
router.post('/shutdown', function (req, res, next) {

  if (req.body.command == "SHUTDOWN"){

    res.header('CALL', '/api/shutdown')
    res.status(201)
    res.json({
      success: true,
      message: 'OK. Shutting down...',
    })

    console.log('[PROFILER] Shutting down...')
    process.exit(1)
  }

  res.header('CALL', '/api/shutdown')
  res.status(201)
  res.json({
    success: false,
    message: 'Invalid Command',
  })

})

module.exports = router