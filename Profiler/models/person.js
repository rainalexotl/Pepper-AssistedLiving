var mongoose = require('mongoose')
var uniqueValidator = require('mongoose-unique-validator')
var Schema = mongoose.Schema

/*
 * Schema
 * ----------------------------------------------------------------------------------------------------
 */

var BackgroundSchema = new Schema({
  eyeColour: { type: String, required: false },
  formerProfession: { type: String, required: false },
  favouriteAnimal: { type: String, required: false },
  wearsGlasses: { type: String, required: false },
  birthplace: { type: String, required: false }
})

var LikesSchema = new Schema({
  type: { type: String, required: false },
  name: { type: String, required: false }
})

var PersonSchema = new Schema({
  name: { type: String, required: true },
  background: [BackgroundSchema],
  likes: [LikesSchema]
})

PersonSchema.plugin(uniqueValidator)

PersonSchema.pre('save', function (next) {
  var person = this

  PersonModel.findOne({name: person.name}, function (err, personExists) {
    if (personExists) {
        return next(new Error('A person with this name already exists.'))
      } else {
        next()
      }
  })
})

var PersonModel = mongoose.model('Person', PersonSchema)

PersonModel.prototype.tolistJSON = function () {
  return {
    id: this._id,
    title: this.title
  }
}

if (!PersonSchema.options.toJSON) PersonSchema.options.toJSON = {}
PersonSchema.options.toJSON.transform = function (doc, ret, options) {
  ret.id = ret._id
  delete ret._id
  return ret
}

module.exports = PersonModel
