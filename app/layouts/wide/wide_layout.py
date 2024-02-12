from app.resources.resource_handler import load_background, load_product_image, load_font
from PIL import ImageDraw

class wideLayout:

    def __init__(self, product_data, dropbox, user_id):
        self.product_name = product_data.product_name.upper().split(", ")
        self.background = load_background("data/input/templates/template-wide.jpeg", user_id, 'wide')
        self.product = load_product_image(self.product_name[len(self.product_name) - 1], dropbox)
        self.price = "R$" + product_data.price
        self.installment = "R$" + product_data.installment[:-2] + "," + product_data.installment[-2:]
    
    def text_wrap(self, text, font, max_width, isTitle=False):
        """ 
        Wrap the text if it's bigger than the template width.
        
        Args:
            text: The full text. (str)
            font: The font object. (Font)
            max_width: The maximum width in px that the text will can be. (Int)
            isTitle: Verify if the text is the Title or no (Boolean)
        
        Return:
            A lines list with length less than or equal to one/two, each item represents 
            a line to draw. (List[str])
        """

        lines = []

        # Return if the text width is smaller than max_width and isn't the title
        if font.getlength(text[:-1]) <= max_width and isTitle == False:
            lines.append(text[:-1]) 
        else:
            words = text.split(' ')  
            i = 0
            while i < len(words):
                line = ''         
                while i < len(words) and font.getlength(line + words[i]) <= max_width:                
                    line = line + words[i] + " "
                    i += 1
                lines.append(line)  
                # Stop if there more than one/two lines and removes clipped features
                if len(lines) > 1:
                    if isTitle:
                        break
                    elif lines[0][-2:] != ', ':
                        temp = lines[0].split(', ')
                        temp = ', '.join(temp[:-1])
                        lines[0] = temp
                        lines.pop()
                    elif lines[0][-2:] == ', ':
                        lines[0] = lines[0][:-2]
                        lines.pop()
                    break  

        return lines
    
    def create_text(self):
        """
        Creates the text on the top of the image.
        
        Return:
            Return True in the end of the process.
        """

        draw = ImageDraw.Draw(self.background)

        titleFont = load_font(90)
        featureFont = load_font(50)

        wrapped_title = self.text_wrap(self.product_name[0], titleFont, 1100, True) # Wrap title based on template width.
        wrapped_features = self.text_wrap(', '.join(self.product_name[1:-1]) + ',', featureFont, 1100) # Wrap features based on template width.

        draw.text((90,90), '\n'.join(wrapped_title), font=titleFont, fill=(255, 255, 255), # Draw text with white fill.
                stroke_width=6, stroke_fill=(0, 0, 0)) # Add black stroke around text for better visibility.
        
        # Calculate text height based on font size and number of lines.
        text_height = titleFont.getbbox('\n'.join(wrapped_title))[3] * len(wrapped_title) + (25 * len(wrapped_title))

        draw.text((90,90 + text_height), '\n'.join(wrapped_features), font=featureFont, fill=(255, 255, 255), # Draw text with white fill.
                stroke_width=6, stroke_fill=(0, 0, 0)) # Add black stroke around text for better visibility.

        return True
    
    def product_create(self):
        """ 
        Resize the Image and put in the template.
                
        Return:
            Return True in the end of the process.
        """

        # Calculate the width and height of the non-transparent region
        cropped_image = self.product.crop(self.product.getbbox())
        
        # Calculate the aspect ratio
        aspect_ratio = cropped_image.width / cropped_image.height

        # Calculate the new height based on the template aspect ratio
        new_width = 780
        new_height = int(new_width / aspect_ratio)

        if new_height > 570:
            new_height = 570
            new_width = int(new_height * aspect_ratio)

        # Resize the product image with the new dimensions
        resized_image = cropped_image.resize((new_width, new_height))

        margin_top =  int(660 - (new_height / 2))
        margin_left = int((self.background.width - new_width) / 2)
        
        self.imageMargin = margin_top + new_height

        position = (margin_left, margin_top) 
        self.background.paste(resized_image, position, mask=resized_image) 
        return True
    
    def create_price(self):
        """ 
        Create the bottom of the text price.
                
        Return:
            Return True in the end of the process.
        """

        draw = ImageDraw.Draw(self.background)

        # Installments discounts text
        draw.text((1500, 970), "PARCELE EM 1X COM", font=load_font(35), fill=(255, 255, 255),
                    stroke_width=6, stroke_fill=(0, 0, 0), anchor="rs")
        draw.text((1500, 1020), "7% DE DESCONTO", font=load_font(50), fill=(255, 255, 255),
                    stroke_width=6, stroke_fill=(0, 0, 0), anchor="rs")
        
        draw.text((1570, 970), "OU ATÉ 3X COM", font=load_font(35), fill=(255, 255, 255),
                    stroke_width=6, stroke_fill=(0, 0, 0), anchor="ls")
        draw.text((1570, 1020), "5% DE DESCONTO", font=load_font(50), fill=(255, 255, 255),
                    stroke_width=6, stroke_fill=(0, 0, 0), anchor="ls") 

        # Price text and polygon
        marginTop = 590

        priceLength = load_font(140).getlength(self.price)
        priceLengthWithoutCents = load_font(140).getlength(self.price[:-2])
        
        draw.polygon([(80, marginTop + 140), (100, marginTop - 30), (priceLength + 150, marginTop - 30), (priceLength + 130, marginTop + 140)], fill=(254, 72, 89))
        draw.text((120, marginTop), f"{self.price[:-2]}", font=load_font(140), fill=(255, 255, 255))
        draw.text((120 + priceLengthWithoutCents, marginTop + 5), f",{self.price[-2:]}", font=load_font(75), fill=(255, 255, 255))
        draw.text((140 + priceLengthWithoutCents, marginTop + 75), "À VISTA", font=load_font(30), fill=(255, 255, 255))

        # Installment price
        draw.text((100, marginTop + 160), f"OU EM ATÉ 12X DE {self.installment}", font=load_font(45), fill=(255, 255, 255),
                  stroke_width=4, stroke_fill=(0, 0, 0))
        
        # Footer text
        draw.text((100, 1000), "Preço válido somente durante o período da promoção ou enquanto houver unidades promocionais disponíveis.",
                  font=load_font(25), fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))

        return True

    def create_layout(self):
        """
        Generates the complete Instagram layout.
        """

        self.product_create()  
        self.create_text()  
        self.create_price()
        return self.background  

    def __call__(self):
        return self.create_layout()


    
