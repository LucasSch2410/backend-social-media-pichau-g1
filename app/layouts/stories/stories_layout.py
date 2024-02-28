from app.resources.resource_handler import load_background, load_product_image, load_font
from PIL import ImageDraw
from fastapi import HTTPException, status

class storiesLayout:

    def __init__(self, product_data, templates_dir):
        self.product_name = product_data.product_name.upper().split(', ')
        self.background = load_background(templates_dir, 'stories')
        self.product = load_product_image(product_data.image_url)
        self.price = str(product_data.price).replace(".", ",").split(",")
        self.installment = product_data.installments
        self.installment_price = "R$" + str(product_data.installments_price).replace(".", ",")
        self.discount = product_data.discount
    
    def text_wrap(self, text, font, max_width, isTitle=False):
        """ 
        Wrap the text if it's bigger than the template width.
        
        Args:
            text: The full text. (str)
            font: The font object. (Font)
            max_width: The maximum width in px that the text will can be. (Int)
            isTitle: Verify if the text is the Title or no (Boolean)
        
        Return:
            A lines list with length less than or equal to 2, each item represents 
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
                # Stop if there more than two lines and removes clipped features
                if len(lines) > 1:
                    if isTitle:
                        break
                    elif lines[1][-2:] != ', ':
                        temp = lines[1].split(', ')
                        temp = ', '.join(temp[:-1])
                        lines[1] = temp
                    elif lines[1][-2:] == ', ':
                        lines[1] = lines[1][:-2]
                    break  
        return lines
    
    def create_text(self):
        """
        Creates the text on the top of the image.

        Global:
            self.text_height: The height of the title/features text. (Int)

        Return:
            Return True in the end of the process.
        """

        draw = ImageDraw.Draw(self.background)

        titleFont = load_font(90)
        featureFont = load_font(50)

        wrapped_title = self.text_wrap(self.product_name[0], titleFont, self.background.width - 200, True) # Wrap title based on template width.
        wrapped_features = self.text_wrap(', '.join(self.product_name[1:-1]) + ',', featureFont, self.background.width - 200) # Wrap features based on template width.
        print(wrapped_title)
        draw.text((110,480), '\n'.join(wrapped_title), font=titleFont, fill=(255, 255, 255), # Draw text with white fill.
                stroke_width=6, stroke_fill=(0, 0, 0)) # Add black stroke around text for better visibility.
        
        # Calculate text height based on font size and number of lines.
        text_height = titleFont.getbbox('\n'.join(wrapped_title))[3] * len(wrapped_title) + (25 * len(wrapped_title))

        draw.text((110,480 + text_height), '\n'.join(wrapped_features), font=featureFont, fill=(255, 255, 255), # Draw text with white fill.
                stroke_width=6, stroke_fill=(0, 0, 0)) # Add black stroke around text for better visibility.

        self.text_height = text_height + featureFont.getbbox('\n'.join(wrapped_features))[3] * len(wrapped_features) + (25 * len(wrapped_features))

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
        new_width = self.background.width - 200
        new_height = int(new_width / aspect_ratio)

        if new_height > 700:
            new_height = 700
            new_width = int(new_height * aspect_ratio)

        # Resize the product image with the new dimensions
        resized_image = cropped_image.resize((new_width, new_height))

        margin_top = int(((1960 + self.text_height) / 2) - new_height / 2) 
        margin_left = int((self.background.width - new_width) / 2)
        
        position = (margin_left, margin_top) 
        self.background.paste(resized_image, position, mask=resized_image) 

        return True
    
    def create_price(self):
        """ 
        Create the bottom of the text price.
                
        Return:
            Return True in the end of the process.
        """

        import re

        draw = ImageDraw.Draw(self.background)
        marginTop = 1500 

        # Installments discounts text
        pattern = r'^(.*?)\b(\d+%.*?)$'
        match = re.match(pattern, self.discount)

        if match:
            discount = match.groups()

            draw.text((1000, marginTop + 90), discount[0].upper().strip(), font=load_font(55), fill=(255, 255, 255),
                        stroke_width=6, stroke_fill=(0, 0, 0), anchor="rs")
            draw.text((1000, marginTop + 150), discount[1].upper().strip(), font=load_font(70), fill=(255, 255, 255),
                        stroke_width=6, stroke_fill=(0, 0, 0), anchor="rs")
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f'Coluna desconto está um padrão incorreto.'
            )
        

        # Price text and polygon
        priceLength = load_font(140).getlength("R$" + ",".join(self.price))
        priceLengthWithoutCents = load_font(140).getlength("R$"+ self.price[0])
        
        draw.polygon([(80, marginTop + 140), (100, marginTop - 30), (priceLength + 160, marginTop - 30), (priceLength + 140, marginTop + 140)], fill=(254, 72, 89))
        draw.text((130, marginTop), f"R${self.price[0]}", font=load_font(140), fill=(255, 255, 255))
        draw.text((140 + priceLengthWithoutCents, marginTop + 5), f",{self.price[1]}", font=load_font(75), fill=(255, 255, 255))
        draw.text((160 + priceLengthWithoutCents, marginTop + 75), "À VISTA", font=load_font(30), fill=(255, 255, 255))

        # Installment price
        draw.text((100, marginTop + 170), f"OU EM ATÉ {self.installment}X DE {self.installment_price}", font=load_font(55), fill=(255, 255, 255),
                  stroke_width=6, stroke_fill=(0, 0, 0))
        
        # Footer text
        draw.text((100, marginTop + 270), "Preço válido somente durante o período da promoção ou enquanto houver unidades promocionais disponíveis.",
                  font=load_font(25), fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))

        return True

    def create_layout(self):
        """
        Generates the complete Instagram layout.
        """

        self.create_text()  
        self.product_create()  
        self.create_price()
        self.product.close()
        return self.background  

    def __call__(self):
        return self.create_layout()


    
