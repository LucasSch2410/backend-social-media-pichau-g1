from app.resources.resource_handler import load_background, load_product_image, load_font
from PIL import ImageDraw

class pushLayout:

    def __init__(self, product_data, templates_dir):
        self.product_name = product_data.product_name.upper().split(', ')
        self.background = load_background(templates_dir, 'push')
        self.product = load_product_image(product_data.image_url)
        self.price = "R$" + str(product_data.price)
        self.installment = "R$" + str(product_data.installments_price)
    
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

        titleFont = load_font(35)
        featureFont = load_font(15)

        wrapped_title = self.text_wrap(self.product_name[0], titleFont, 450, True) # Wrap title based on template width.
        wrapped_features = self.text_wrap(', '.join(self.product_name[1:-1]) + ',', featureFont, 450) # Wrap features based on template width.

        draw.text((25, 25), '\n'.join(wrapped_title), font=titleFont, fill=(255, 255, 255), # Draw text with white fill.
                stroke_width=3, stroke_fill=(0, 0, 0)) # Add black stroke around text for better visibility.
        
        # Calculate text height based on font size and number of lines.
        text_height = titleFont.getbbox('\n'.join(wrapped_title))[3] * len(wrapped_title) + (10 * len(wrapped_title))

        draw.text((25, 25 + text_height), '\n'.join(wrapped_features), font=featureFont, fill=(255, 255, 255), # Draw text with white fill.
                stroke_width=2, stroke_fill=(0, 0, 0)) # Add black stroke around text for better visibility.

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
        new_width = 350
        new_height = int(new_width / aspect_ratio)

        if new_height > 220:
            new_height = 220
            new_width = int(new_height * aspect_ratio)

        # Resize the product image with the new dimensions
        resized_image = cropped_image.resize((new_width, new_height))

        margin_top = int(220 - (new_height / 2))
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
        draw.text((690, 220), "PARCELE EM 1X COM", font=load_font(20), fill=(255, 255, 255),
                    stroke_width=2, stroke_fill=(0, 0, 0), anchor="ra")
        draw.text((690, 240), "7% DE DESCONTO", font=load_font(25), fill=(255, 255, 255),
                    stroke_width=2, stroke_fill=(0, 0, 0), anchor="ra")
        
        draw.text((690, 270), "OU ATÉ 3X COM", font=load_font(20), fill=(255, 255, 255),
                    stroke_width=2, stroke_fill=(0, 0, 0), anchor="ra")
        draw.text((690, 290), "5% DE DESCONTO", font=load_font(25), fill=(255, 255, 255),
                    stroke_width=2, stroke_fill=(0, 0, 0), anchor="ra")
        
        # Price text and polygon
        marginTop = 230 

        priceLength = load_font(75).getlength(self.price)
        priceLengthWithoutCents = load_font(75).getlength(self.price[:-3])
        
        draw.polygon([(30, marginTop + 75), (36, marginTop), (priceLength + 44, marginTop), (priceLength + 40, marginTop + 75)], fill=(254, 72, 89))
        draw.text((45, marginTop + 6), f"{self.price[:-3]}", font=load_font(75), fill=(255, 255, 255))
        draw.text((45 + priceLengthWithoutCents, marginTop + 10), f",{self.price[-2:]}", font=load_font(42), fill=(255, 255, 255))
        
        # Footer text
        draw.text((360, 330), "Preço válido somente durante o período da promoção ou enquanto houver unidades promocionais disponíveis.",
                  font=load_font(15), fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0), anchor='ma')

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


    
