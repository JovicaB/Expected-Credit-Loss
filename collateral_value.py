class Collateral:
    def __init__(self):
        self.dict_collateral = None
        self.output = None

    def collateral_values(self):
        """
        calculates weighted average based on selling percentage of collateral value weighted exponentially
        so that later years have advantage
        :return: list of weighted average collateral values
        """
        collateral_raw = self.collateral_raw_values()
        collateral_ponders = self.collateral_ponders()

        self.output = {key: round(sum(value[i] * collateral_ponders[i] for i in range(len(value))), 2)
                       for key, value in collateral_raw.items()}

        return self.output

    def collateral_raw_values(self):
        """
        reads collateral activation percentages from collateral database
        :return: dictionary of collateral activation percentages
        """
        self.dict_collateral = Collateral.collateral_dt_to_dict(
            'data/collateral_data.db', 'collateral')

        return self.dict_collateral

    def collateral_ponders(self):
        """
        method that returns list of ponder values distributed reverse exponentially
        :return: list of collateral ponder values
        """
        collateral_ponders = [0.7976, 0.0893, 0.0299, 0.0173, 0.0131, 0.0115, 0.0107, 0.0103, 0.0102, 0.0101]
        return collateral_ponders

    @staticmethod
    def collateral_dt_to_dict(path, table_name):
        """
        function that converts SQL data_table to nested dictionary [main key = row number, key = column name, value]
        """
        with sqlite3.connect(path) as db:
            cursor = db.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            names = [keys[0] for keys in cursor.description][1:]
            raw_dict = {row[0]: dict(zip(names, row[1:]))
                        for row in cursor.fetchall()}

            result = {'A': [], 'B': [], 'C': [], 'D': []}
            for year_dict in raw_dict.values():
                result['A'].append(year_dict['A'])
                result['B'].append(year_dict['B'])
                result['C'].append(year_dict['C'])
                result['D'].append(year_dict['D'])
            return result
