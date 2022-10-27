# Working with SQL 

_This section requires a Practicus AI cloud node. Please visit the [introduction to cloud nodes](cloud-intro.md) section of this tutorial to learn more._

## Using SQL with a SQL database 

This is quite straightforward, if the database you connect to support SQL, you can simply _start_ by authoring a SQL statement. 

Practicus AI cloud nodes come with a simple music artists database.

- Open _Explore_ tab
- Select a _Cloud Node_ upper right of screen (start new or reuse existing)
- Select _SQLite_ on the left menu 
- Click _Run Query_

You will see the result of a sample SQL, feel free to experiment and rerun the SQL

![](img/sql/sqlite.png)

As you will see later in this tutorial, Practicus AI also allows you to run SQL on the result of your previous SQL, as many times as you need. On a SQL database you would need to use temporary tables to do so, which is a relatively advanced topic.

## Using SQL on any data

Practicus AI allows you to use SQL _without_ a SQL database. Let's demonstrate using an Excel file. You can do the same on other non-SQL data, such as S3. 

- Open _Explore_ tab
- Select _Local Files_
- Load Home > practicus > samples > data > node_types.xlsx

![](img/sql/load.png)

- Click on _SQL Query_ button

![](img/sql/sql-1.png)

Since SQL is an advanced feature, it will require a cloud node to run. You will be asked if you would like to quickly upload to a cloud node. Click Yes, select a cloud node, and now your Excel file will be on the cloud. 

Click on _SQL Query_ button again. This time the SQL query editor will be displayed.

- Type the below SQL 

```sql
SELECT "Name", "Total price", "Bang for buck" 
FROM "node_types" 
WHERE "Total price" < 5
ORDER BY "Bang for buck" DESC
```

Tip: double-clicking on a column name adds its name to the query editor, so you can write SQL faster. If you select some text before double-clicking, your selected text is replaced with the column name.

- Click on _Test SQL_ button

Note: Your first SQL on a particular cloud node (cold run) will take a little longer to run. Subsequent SQL queries will run instantly. 

![](img/sql/sql-2.png)

- (Optional) Experiment further with the SQL, click
- When ready, click _Apply SQL_ button

You will get the result of the SQL back in the worksheet.  

## (Optional) Visualize SQL result

- Click Analyze > Graph
- Select _Bang for buck_ for X and _Total Price_ for Y
- Click ok

![](img/sql/sql-3.png)

You will see the **estimated** total cost (Practicus AI license cost + Cloud infrastructure cost), and how much cloud capacity **value** you would expect to get (bang for buck) visualized. 

![](img/sql/sql-graph.png)

Note: If you have Practicus AI Enterprise license, your software is already paid for. So this graph would not make any sense.  This is only meaningful for the professional pay-as-you-go license type.

[< Previous](predict.md) | [Next >](next-steps.md)