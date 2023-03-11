from input import Collateral
import sqlite3


class CreditPortfolio:
    def __init__(self, row_index):
            self.row_index = row_index

    @property
    def credit_portfolio_data(self):
        """
        converts SQL data_table to nested dictionary
        [main key = row number, key = column name, value]
        """
        with sqlite3.connect('data/credit_portfolio.db') as db:
            cursor = db.cursor()
            cursor.execute(f"SELECT * FROM portfolio")
            portfolio_data = cursor.fetchall()
            return {data[0]: data[1:] for data in portfolio_data}
            # return [description[0] for description in cursor.description]

    def credit_ead(self):
        """
        :return: Exposure at Default
        """
        return self.credit_portfolio_data[self.row_index][1]

    def collateral_liquidation_value(self):
        """
        liquidation value for lgd calculation based on 10 year collateral activation values pondered exponentially
        :return:
        """
        collateral_value = self.credit_portfolio_data[self.row_index][5]
        collateral_liquidation_value = Collateral().collateral_values()[self.credit_portfolio_data[self.row_index][6]]
        return collateral_value * collateral_liquidation_value

    def credit_lgd(self):
        """
        :return: Loss Given Default
        """
        return self.collateral_liquidation_value() / self.credit_ead()

    def credit_pd(self):
        """
        :return: Probability of default
        """
        return self.credit_portfolio_data[self.row_index][7]

    def credit_ecl(self):
        """
        EAD * LGD * PD
        :return: Expected Credit Loss
        """
        return self.credit_ead() * self.credit_lgd() * self.credit_pd()

    def credit_table_data(self):
        """
        credit table data
        :return: list of lists [id, creditor name, credit_value, credit_life, risk, lgd, ecl]
        """
        db_data = self.credit_portfolio_data
        db_data_keys = db_data.keys()

        table_data = []

        for key in db_data_keys:
            row_data = [
                key,
                db_data[key][0],
                db_data[key][1],
                db_data[key][3],
                round(db_data[key][7] * 100, 2),
                round(CreditPortfolio(key).credit_lgd() * 100, 2),
                CreditPortfolio(key).credit_ecl(),
            ]
            table_data.append(row_data)

        return table_data


class Statistics:
    def __init__(self):
        self.data = CreditPortfolio(1).credit_portfolio_data

    def credit_value_total(self):
        """
        :return: total value of credit porfolio
        """
        portfolio_data = self.data
        return sum([credit_value[1] for credit_value in portfolio_data.values()])

    def credit_multiplier(self, credit_value):
        """
        :return:share of credit value in credit value portfolio
        """
        return credit_value / self.credit_value_total()

    def statistics_lgd(self):
        """
        :return: total lgd adjusted by share of individual credit in credit portfolio
        """
        return round(sum([self.credit_multiplier(lgd[2]) * lgd[5]/100 for lgd in CreditPortfolio(1).credit_table_data()]) * 100)

    def statistics_ecl(self):
        """
        :return: total ecl adjusted by share of individual credit in credit portfolio
        """
        return round(sum([ecl[6] for ecl in CreditPortfolio(1).credit_table_data()]))

    def statistics_data(self):
        """
        :return: data for statistics table
        """
        stat_data = [
            len(self.data.keys()),
            round(self.credit_value_total()),
            round(sum([risk[7] * self.credit_multiplier(risk[1]) for risk in self.data.values()]), 2),
            self.statistics_lgd(),
            self.statistics_ecl()
        ]
        return stat_data
