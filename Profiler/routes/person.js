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
 * Params: forename (req.body.forename)
 */
router.post('/add/likeDislike', function (req, res, next) {

  Person.findOne({ forename: req.body.forename }, function (err, person){
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
  });

})

/* 
 * Method: POST
 * Behav.: Gets all likes for a given user
 * 
 * Params: forename (req.body.forename)
 */
router.post('/likes', function (req, res, next) {

  Person.findOne({ forename: req.body.forename }, function (err, person){

    Person.aggregate([{ $project: { likesDislikes: 1 } }, { $unwind: '$likesDislikes' }, { $match: { "likesDislikes.likeDislike": true } }]).exec((err, likes) => {
      if(err) {
        res.status(400)
        return res.json({
          success: false,
          message: err.message
        })
      }
  
      var arrayLikes = []
      for(i = 0; i < likes.length; i++){
        arrayLikes.push({"thing":likes[i].likesDislikes.thing});
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

module.exports = router