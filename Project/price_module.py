class Pricing_module:
    def __init__(self):
        self.current_price = 1.5
        self.company_profit_factor = 0.1 # 10%

        self.price_p_gallon = 0


    def calcPrice(self, location, hist, gal_requested):
        location_factor = 0.04
        if location.lower() == 'tx':
            location_factor = 0.02

        hist_factor = 0        
        if hist == 'yes':
            hist_factor = 0.01

        gal_req_factor = 0.03
        if gal_requested > 1000:
            gal_req_factor = 0.02
        
        margin = self.current_price * (location_factor - hist_factor + \
                gal_req_factor + self.company_profit_factor)
        
        self.price_p_gallon = self.current_price + margin
        
        return self.price_p_gallon
        
            
        
        
