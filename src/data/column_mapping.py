import pandas as pd

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza nombres de columnas según el estándar único del sistema.
    - 'Stagnation': periodo de estancamiento (tiempo o trades sin nuevo máximo de equity).
    - 'Stagnation_Trades': número máximo de operaciones consecutivas en estancamiento (si la fuente lo provee).
    """
    column_mapping = {
        # Integrales
        'Strategy Name': 'Strategy_Name',
        'Profit Factor': 'Profit_factor',
        'Profit factor': 'Profit_factor',
        'Sharpe Ratio': 'Sharpe_Ratio',
        'CalmarRatio': 'CalmarRatio',
        'Max DD %': 'Max_DD_%',
        'Drawdown': 'Max_DD_%',
        'Stagnation (Trades)': 'Stagnation',
        'Avg. Stagnation Trades': 'Stagnation',
        'Max Stagnation Trades': 'Stagnation_Trades',
        'Stagnation_Trades': 'Stagnation_Trades',
        '# of trades': '#_of_trades',
        'Avg. Bars in Trade': 'Avg_Bars_in_Trade',
        'Ulcer Index %': 'Ulcer_Index_%',
        'VaR (95%)': 'VaR_95%',
        'CVaR (95%)': 'CVaR_95%',
        'Winning Percent': 'Winning_Percent',
        'Max Consec. Losses': 'Max_Consec_Losses',
        'Payout ratio': 'Payout_ratio',
        'Sortino Ratio': 'Sortino_Ratio',
        'RecoveryFactor': 'RecoveryFactor',
        'RINAIndex': 'RINAIndex',
        'Ulcer Performance Index': 'Ulcer_Performance_Index',
        'SQN': 'SQN',
        'Net profit': 'Net_profit',
        'Expectancy': 'Expectancy',
        'Exposure': 'Exposure',
        'CAGR': 'CAGR',
        'Total Data Months': 'Total_Data_Months',
        'Max Drawdown Duration': 'Max_Drawdown_Duration',
        'New Peak Trades %': 'New_Peak_Trades_%',
        'Drawdown Trades %': 'Drawdown_Trades_%',
        # IS
        'Sharpe Ratio (IS)': 'Sharpe_Ratio_IS',
        'Profit factor (IS)': 'Profit_Factor_IS',
        'CalmarRatio (IS)': 'CalmarRatio_IS',
        'Winning Percent (IS)': 'Winning_Percent_IS',
        'CAGR (IS)': 'CAGR_IS',
        'Drawdown (IS)': 'Max_Drawdown_IS',
        # OOS
        'Sharpe Ratio (OOS)': 'Sharpe_Ratio_OOS',
        'Profit factor (OOS)': 'Profit_Factor_OOS',
        'CalmarRatio (OOS)': 'CalmarRatio_OOS',
        'Winning Percent (OOS)': 'Winning_Percent_OOS',
        'CAGR (OOS)': 'CAGR_OOS',
        'Drawdown (OOS)': 'Max_Drawdown_OOS',
        # Mapeos adicionales para compatibilidad
        'WINRATE': 'Winning_Percent',
        'WIN_RATE': 'Winning_Percent',
        'PROFIT_FACTOR': 'Profit_Factor',
        'PF': 'Profit_Factor',
        'SHARPE': 'Sharpe_Ratio',
        'SHARPE_RATIO': 'Sharpe_Ratio',
        'DRAWDOWN': 'Max_Drawdown',
        'MAX_DD': 'Max_Drawdown',
        'NET_PROFIT': 'Net_Profit'
    }
    df_normalized = df.copy()
    df_normalized.columns = [column_mapping.get(col.strip().replace('"','').replace("'",''),
                                              col.strip().replace(' ','_').replace('"','').replace("'",''))
                            for col in df_normalized.columns]
    return df_normalized 