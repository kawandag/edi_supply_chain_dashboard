from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, datediff, lit, when
import sys

input_prefix = sys.argv[1]  # s3://bucket/processed/
output_prefix = sys.argv[2] # s3://bucket/analytics/

spark = SparkSession.builder.appName("sc-edi-analytics").getOrCreate()
df = spark.read.json(input_prefix + "*.json")

invoices = df.filter(col("type")=="invoice").select("invoice_id","partner_id","partner_name","po_id","invoice_date","amount","terms")
payments = df.filter(col("type")=="payment").select("payment_id","partner_id","invoice_id","payment_date","amount")

invoices = invoices.withColumn("invoice_date", to_date(col("invoice_date"), "yyyy-MM-dd"))
payments = payments.withColumn("payment_date", to_date(col("payment_date"), "yyyy-MM-dd"))

joined = invoices.join(payments, on="invoice_id", how="left")
joined = joined.withColumn("days_to_pay", datediff(col("payment_date"), col("invoice_date")))
joined = joined.withColumn("is_late", when(col("payment_date").isNull(), True).otherwise(
    when(datediff(col("payment_date"), col("invoice_date")) > col("terms"), True).otherwise(False)
))

joined.coalesce(1).write.option("header",True).csv(output_prefix + "invoices_enriched/")

agg = joined.groupBy("partner_id","partner_name").agg(
).agg({"invoice_id":"count","is_late":"sum","days_to_pay":"avg","amount":"avg"})  .withColumnRenamed("count(invoice_id)","total_invoices")  .withColumnRenamed("sum(is_late)","late_invoices")  .withColumnRenamed("avg(days_to_pay)","avg_days_to_pay")  .withColumnRenamed("avg(amount)","avg_invoice_amount")

agg = agg.withColumn("late_rate", col("late_invoices")/col("total_invoices"))
agg = agg.withColumn("risk_score", (col("avg_days_to_pay")/lit(60)) + col("late_rate"))
agg.coalesce(1).write.option("header",True).csv(output_prefix + "supplier_metrics/")
spark.stop()
