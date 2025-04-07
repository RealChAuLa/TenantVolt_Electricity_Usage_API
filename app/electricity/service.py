from datetime import datetime, timedelta
import calendar
import logging
from typing import List
from fastapi.logger import logger
from app.db.firebase import database
from app.electricity.models import ChartDataPoint, ChartDataResponse,  BillResponse ,TenantRequest, TenantStatusResponse


class ElectricityUsageService:
    @staticmethod
    def get_minutely_usage(product_id: str, date_str: str, hour: str) -> ChartDataResponse:
        """Get minutely average electricity usage for a specific hour in a day."""
        try:
            # Access the Firebase path for the specific product, date, and hour
            ref_path = f"electricity_usage/{product_id}/{date_str}/{hour}"
            minute_data = database.child(ref_path).get() or {}

            # Convert to chart data points sorted by minute
            data_points = []

            # Handle both object format and array format data
            if isinstance(minute_data, dict):
                # Process dictionary-style data (minute: value)
                for minute, value in sorted(minute_data.items()):
                    # Skip null values and ensure we have a valid float
                    if value is not None:
                        try:
                            watt_value = float(value)
                            data_points.append(ChartDataPoint(
                                label=minute,
                                value=round(watt_value, 2)
                            ))
                        except (ValueError, TypeError):
                            # Skip invalid values
                            logger.warning(f"Invalid value for minute {minute}: {value}")
            elif isinstance(minute_data, list):
                # Process array-style data where index is the minute
                for index, value in enumerate(minute_data):
                    # Skip null values
                    if value is not None:
                        try:
                            watt_value = float(value)
                            minute_str = f"{index:02d}"
                            data_points.append(ChartDataPoint(
                                label=minute_str,
                                value=round(watt_value, 2)
                            ))
                        except (ValueError, TypeError):
                            # Skip invalid values
                            logger.warning(f"Invalid value for minute {index}: {value}")

            return ChartDataResponse(
                data_points=data_points,
                chart_title=f"Minute-by-Minute Usage on {date_str} at {hour}:00",
                x_axis_label="Minute"
            )
        except Exception as e:
            logger.error(f"Error retrieving minutely data: {str(e)}")
            return ChartDataResponse(
                data_points=[],
                chart_title=f"No data available for {date_str} at {hour}:00",
                x_axis_label="Minute"
            )

    @staticmethod
    def get_hourly_usage(product_id: str, date_str: str) -> ChartDataResponse:
        """Get hourly average electricity usage for a specific day."""
        try:
            # Access the Firebase path for the specific product and date
            ref_path = f"electricity_usage/{product_id}/{date_str}"
            day_data = database.child(ref_path).get() or {}

            data_points = []

            # Process each hour in the day
            for hour in sorted(day_data.keys()):
                # Skip non-hour keys like "connection_status"
                if not hour.isdigit():
                    continue

                hour_data = day_data.get(hour, {})
                hour_values = []

                # Handle both object format and array format data
                if isinstance(hour_data, dict):
                    # Dictionary format (minute: value)
                    for minute, value in hour_data.items():
                        if value is not None:
                            try:
                                hour_values.append(float(value))
                            except (ValueError, TypeError):
                                continue
                elif isinstance(hour_data, list):
                    # Array format where index is the minute
                    for value in hour_data:
                        if value is not None:
                            try:
                                hour_values.append(float(value))
                            except (ValueError, TypeError):
                                continue

                # Calculate the hour's average if we have values
                if hour_values:
                    hour_avg = sum(hour_values) / len(hour_values)
                    data_points.append(ChartDataPoint(
                        label=f"{hour}:00",
                        value=round(hour_avg, 2)
                    ))

            return ChartDataResponse(
                data_points=data_points,
                chart_title=f"Hourly Usage on {date_str}",
                x_axis_label="Hour"
            )
        except Exception as e:
            logger.error(f"Error retrieving hourly data: {str(e)}")
            return ChartDataResponse(
                data_points=[],
                chart_title=f"No data available for {date_str}",
                x_axis_label="Hour"
            )

    @staticmethod
    def get_daily_usage(product_id: str, year_month: str) -> ChartDataResponse:
        """Get daily average electricity usage for a specific month."""
        try:
            # Extract year and month from input
            year, month = year_month.split('-')

            # Calculate the number of days in the month
            _, days_in_month = calendar.monthrange(int(year), int(month))

            data_points = []

            # For each day in the month
            for day in range(1, days_in_month + 1):
                # Format the date string for Firebase
                date_str = f"{year_month}-{day:02d}"

                try:
                    # Get data for the day
                    day_ref_path = f"electricity_usage/{product_id}/{date_str}"
                    day_data = database.child(day_ref_path).get()

                    if not day_data:
                        continue  # Skip if no data for this day

                    # Calculate the daily average across all hours and minutes
                    all_values = []

                    for hour, hour_data in day_data.items():
                        # Skip non-hour keys
                        if not hour.isdigit():
                            continue

                        # Process each minute in the hour
                        if isinstance(hour_data, dict):
                            for minute, value in hour_data.items():
                                if value is not None:
                                    try:
                                        all_values.append(float(value))
                                    except (ValueError, TypeError):
                                        continue
                        elif isinstance(hour_data, list):
                            for value in hour_data:
                                if value is not None:
                                    try:
                                        all_values.append(float(value))
                                    except (ValueError, TypeError):
                                        continue

                    # Add data point if we have values
                    if all_values:
                        daily_avg = sum(all_values) / len(all_values)
                        data_points.append(ChartDataPoint(
                            label=f"{day:02d}",
                            value=round(daily_avg, 2)
                        ))
                except Exception as e:
                    logger.warning(f"Error processing day {date_str}: {str(e)}")
                    continue  # Skip this day if there's an error

            # Get month name for the chart title
            month_name = datetime.strptime(month, "%m").strftime("%B")

            return ChartDataResponse(
                data_points=data_points,
                chart_title=f"Daily Usage in {month_name} {year}",
                x_axis_label="Day"
            )
        except Exception as e:
            logger.error(f"Error retrieving daily data: {str(e)}")
            return ChartDataResponse(
                data_points=[],
                chart_title=f"No data available for {year_month}",
                x_axis_label="Day"
            )

    @staticmethod
    def get_monthly_usage(product_id: str, year: str) -> ChartDataResponse:
        """Get monthly average electricity usage for a specific year."""
        try:
            data_points = []

            # For each month in the year
            for month in range(1, 13):
                month_str = f"{month:02d}"

                try:
                    # Get all data for the month
                    month_ref_path = f"electricity_usage/{product_id}"
                    year_month = f"{year}-{month_str}"

                    # Get all days for this month
                    all_month_values = []

                    # For each day in the month
                    _, days_in_month = calendar.monthrange(int(year), int(month))
                    for day in range(1, days_in_month + 1):
                        date_str = f"{year_month}-{day:02d}"
                        day_ref_path = f"{month_ref_path}/{date_str}"
                        day_data = database.child(day_ref_path).get()

                        if not day_data:
                            continue  # Skip if no data for this day

                        # Process each hour in the day
                        for hour, hour_data in day_data.items():
                            # Skip non-hour keys
                            if not hour.isdigit():
                                continue

                            # Process each minute in the hour
                            if isinstance(hour_data, dict):
                                for minute, value in hour_data.items():
                                    if value is not None:
                                        try:
                                            all_month_values.append(float(value))
                                        except (ValueError, TypeError):
                                            continue
                            elif isinstance(hour_data, list):
                                for value in hour_data:
                                    if value is not None:
                                        try:
                                            all_month_values.append(float(value))
                                        except (ValueError, TypeError):
                                            continue

                    # Calculate monthly average if we have values
                    if all_month_values:
                        monthly_avg = sum(all_month_values) / len(all_month_values)

                        # Get month name for the label
                        month_name = datetime.strptime(month_str, "%m").strftime("%b")
                        data_points.append(ChartDataPoint(
                            label=month_name,
                            value=round(monthly_avg, 2)
                        ))
                except Exception as e:
                    logger.warning(f"Error processing month {year_month}: {str(e)}")
                    continue  # Skip this month if there's an error

            return ChartDataResponse(
                data_points=data_points,
                chart_title=f"Monthly Usage in {year}",
                x_axis_label="Month"
            )
        except Exception as e:
            logger.error(f"Error retrieving monthly data: {str(e)}")
            return ChartDataResponse(
                data_points=[],
                chart_title=f"No data available for {year}",
                x_axis_label="Month"
            )

    @staticmethod
    def calculate_billing_tiers(total_kwh: float) -> float:
        """Calculate the bill amount based on the tiered pricing structure."""
        tiers = [
            (30, 195.00),
            (60, 500.00),
            (90, 1480.00),
            (120, 2680.00),
            (150, 4170.00),
            (180, 5160.00),
            (210, 7220.00),
            (240, 8780.00),
            (270, 10340.00),
            (300, 11900.00)
        ]

        # Find the appropriate tier
        for units, price in tiers:
            if total_kwh <= units:
                # Calculate the bill amount by dividing the tier price by the tier's max units
                # and then multiplying by the actual kWh used
                unit_price = price / units
                return unit_price * total_kwh

        # If above the highest tier, use the highest tier's unit price
        highest_units, highest_price = tiers[-1]
        unit_price = highest_price / highest_units
        return unit_price * total_kwh

    @staticmethod
    def calculate_total_kwh_for_month(product_id: str, year_month: str) -> float:
        """Calculate the total kWh used in a month."""
        try:
            year, month = year_month.split('-')
            _, days_in_month = calendar.monthrange(int(year), int(month))

            # Track the total watt-hours for the month
            total_watt_hours = 0

            # Loop through all days in the month
            for day in range(1, days_in_month + 1):
                date_str = f"{year_month}-{day:02d}"

                # Get data for this day
                day_ref_path = f"electricity_usage/{product_id}/{date_str}"
                day_data = database.child(day_ref_path).get() or {}

                # Loop through all hours in the day
                for hour, hour_data in day_data.items():
                    if not hour.isdigit():
                        continue  # Skip non-hour keys

                    # Calculate the average watts for this hour
                    hour_watt_values = []

                    # Process minutes
                    if isinstance(hour_data, dict):
                        for minute, watt_value in hour_data.items():
                            if watt_value is not None:
                                try:
                                    hour_watt_values.append(float(watt_value))
                                except (ValueError, TypeError):
                                    continue
                    elif isinstance(hour_data, list):
                        for minute_value in hour_data:
                            if minute_value is not None:
                                try:
                                    hour_watt_values.append(float(minute_value))
                                except (ValueError, TypeError):
                                    continue

                    # If we have values for this hour, calculate the average and add to total watt-hours
                    if hour_watt_values:
                        avg_watts_for_hour = sum(hour_watt_values) / len(hour_watt_values)
                        # Add one hour's worth of energy at this power level
                        total_watt_hours += avg_watts_for_hour

            # Convert watt-hours to kilowatt-hours
            total_kwh = total_watt_hours / 1000

            return round(total_kwh, 2)
        except Exception as e:
            logger.error(f"Error calculating kWh for {year_month}: {str(e)}")
            return 0.0

    @staticmethod
    def generate_bill(username: str) -> BillResponse:
        """Generate a bill for the past month if it's not already paid."""
        try:
            # Get current date and extract last month
            current_date = datetime.utcnow()
            first_day_of_current_month = current_date.replace(day=1)
            last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
            last_month = last_day_of_last_month.strftime("%Y-%m")

            # Get user's product ID (needed for both paid and unpaid cases)
            user_ref_path = f"user_details/{username}"
            user_data = database.child(user_ref_path).get() or {}

            product_id = user_data.get("product_id", "")
            if not product_id:
                raise ValueError(f"No product_id found for user {username}")

            # Calculate total kWh for last month (needed for both paid and unpaid cases)
            total_kwh = ElectricityUsageService.calculate_total_kwh_for_month(product_id, last_month)

            # Check if bill is already paid
            payments_ref_path = f"user_details/{username}/payments"
            payments_data = database.child(payments_ref_path).get() or {}

            is_paid = last_month in payments_data

            if is_paid:
                # Get the actual payment amount from the database
                payment_amount = payments_data.get(last_month)
                try:
                    payment_amount = float(payment_amount)
                except (ValueError, TypeError):
                    payment_amount = 0.0

                # Return a response indicating the bill is already paid, but include the calculated kWh
                return BillResponse(
                    username=username,
                    year_month=last_month,
                    total_kwh=total_kwh,  # Include the actual calculated kWh
                    amount=payment_amount,
                    is_paid=True,
                    message=f"Bill for {last_month} has already been paid."
                )
            else:
                # If not paid, use the calculated kWh to determine the bill amount
                bill_amount = ElectricityUsageService.calculate_billing_tiers(total_kwh)

                return BillResponse(
                    username=username,
                    year_month=last_month,
                    total_kwh=total_kwh,
                    amount=bill_amount,
                    is_paid=False,
                    message=f"Unpaid bill for {last_month}. Please make a payment."
                )
        except Exception as e:
            logger.error(f"Error generating bill for {username}: {str(e)}")
            return BillResponse(
                username=username,
                year_month="Unknown",
                total_kwh=0.0,
                amount=0.0,
                is_paid=False,
                message=f"Error generating bill: {str(e)}"
            )


class ConnectionService:
    @staticmethod
    async def get_connection_statuses(tenants: List[TenantRequest]) -> List[TenantStatusResponse]:
        """
        Get connection statuses for multiple product IDs
        """
        result = []

        for tenant in tenants:
            try:
                # Get connection status from Firebase
                connection_status = database.child(f"electricity_usage/{tenant.product_id}/connection_status").get()

                # Handle the case where connection_status might be None or has a .val() method
                if hasattr(connection_status, 'val'):
                    connection_status = connection_status.val()

                # If status is None, default to False
                connection_status = bool(connection_status) if connection_status is not None else False

                result.append(TenantStatusResponse(
                    tenant_index=tenant.tenant_index,
                    connection_status=connection_status
                ))

            except Exception as e:
                logging.error(f"Error retrieving connection status for product {tenant.product_id}: {str(e)}")
                # In case of error, assume device is disconnected
                result.append(TenantStatusResponse(
                    tenant_index=tenant.tenant_index,
                    connection_status=False
                ))

        return result

    @staticmethod
    async def update_connection_status(product_id: str, connection_status: bool) -> bool:
        """
        Update connection status for a product ID
        Returns True if successful, False otherwise
        """
        try:
            # Update connection status in Firebase
            database.child(f"electricity_usage/{product_id}/connection_status").set(connection_status)
            return True
        except Exception as e:
            logging.error(f"Error updating connection status for product {product_id}: {str(e)}")
            return False