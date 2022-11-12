from wtforms import Form,form, SubmitField,IntegerField,FloatField,StringField,TextAreaField,validators,DecimalField
from flask_wtf.file import FileField,FileRequired,FileAllowed

class Addproducts(Form):
    name = StringField('Name', [validators.DataRequired()])
    price = FloatField('Price', [validators.DataRequired()])
    discount = IntegerField('Discount', default=0)
    stock = IntegerField('Stock', [validators.DataRequired()])
    colors = StringField('Colors', [validators.DataRequired()])
    discription = TextAreaField('Discription', [validators.DataRequired()])

    image_1 = FileField('Image 1', validators=[FileRequired(), FileAllowed(['jpg','png','gif','jpeg'],'images only please')])
    image_2 = FileField('Image 2', validators=[FileRequired(), FileAllowed(['jpg','png','gif','jpeg'],'images only please')])
    image_3 = FileField('Image 3', validators=[FileRequired(), FileAllowed(['jpg','png','gif','jpeg'],'images only please')])