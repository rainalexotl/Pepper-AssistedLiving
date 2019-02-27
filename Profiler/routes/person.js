const express = require('express')
const router = express.Router()
const mongoose = require('mongoose')

const Person = require('../models/person')

const handleError = error => {
  return console.log(error)
}

// Test
router.get('/test', function (req, res, next) {
  res.header('Location', `/api/person/test`)
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
    
        res.header('Location', `/api/person/addPerson`)
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

  Person.findOne({ name: req.body.forename }, function (err, person){
    var newLikeDislike = { likeDislike: req.body.likeDislike, thing: req.body.thing}

    person.likesDislikes.push(newLikeDislike)

    console.log(person)
    person.save(function (err, p) {
      if (err) {
        res.status(400)
        return res.json({
          success: false,
          message: err.message
        })
      }
  
      res.header('Location', `/api/person/likeDislike`)
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
 * Method: GET
 * Behav.: Gets all likes for a given user
 * 
 * Params: forename (req.body.forename)
 */
router.get('/person/likes', function (req, res, next) {
  
})

module.exports = router