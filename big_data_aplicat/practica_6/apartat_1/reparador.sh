#!/bin/bash
# hdfs_repair.sh - Script to repair HDFS datanode issues
# Usage: bash hdfs_repair.sh

echo "===== HDFS Repair Tool ====="
echo "This script will attempt to repair common HDFS issues"
echo

# Step 1: Stop HDFS services
echo "1️⃣ Stopping HDFS services..."
$HADOOP_HOME/sbin/stop-dfs.sh
echo "✅ HDFS services stopped"
echo

# Step 2: Clean up temporary files
echo "2️⃣ Removing temporary files..."
rm -rf $HADOOP_HOME/logs/*.log
find $HADOOP_HOME -name "*.pid" -delete
echo "✅ Temporary files cleaned"
echo

# Step 3: Check excluded nodes file
EXCLUDES_FILE="$HADOOP_HOME/etc/hadoop/dfs.exclude"
echo "3️⃣ Checking for excluded nodes file..."
if [ -f "$EXCLUDES_FILE" ]; then
    echo "Found excludes file: $EXCLUDES_FILE"
    echo "Current content:"
    cat "$EXCLUDES_FILE"
    echo
    
    # Empty the excludes file
    echo "Emptying excludes file..."
    echo "" > "$EXCLUDES_FILE"
    echo "✅ Excludes file reset"
else
    echo "✅ No excludes file found"
fi
echo

# Step 4: Modify HDFS configuration
echo "4️⃣ Checking HDFS configuration..."
HDFS_SITE="$HADOOP_HOME/etc/hadoop/hdfs-site.xml"

# Create backup of hdfs-site.xml
cp "$HDFS_SITE" "${HDFS_SITE}.bak"
echo "Created backup: ${HDFS_SITE}.bak"

# Modify configuration to address datanode exclusion
echo "Modifying HDFS configuration..."
cat > "$HDFS_SITE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.namenode.replication.min</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.namenode.secondary.http-address</name>
        <value>localhost:9868</value>
    </property>
    <property>
        <name>dfs.webhdfs.enabled</name>
        <value>true</value>
    </property>
    <property>
        <name>dfs.datanode.address</name>
        <value>0.0.0.0:9866</value>
    </property>
    <property>
        <name>dfs.datanode.http.address</name>
        <value>0.0.0.0:9864</value>
    </property>
    <property>
        <name>dfs.client.use.datanode.hostname</name>
        <value>false</value>
    </property>
    <property>
        <name>dfs.datanode.use.datanode.hostname</name>
        <value>false</value>
    </property>
    <!-- Reset excluded nodes -->
    <property>
        <name>dfs.hosts.exclude</name>
        <value></value>
    </property>
    <!-- Fixed block corruption issues -->
    <property>
        <name>dfs.block.scanner.volume.errors.threshold</name>
        <value>0.5</value>
    </property>
    <!-- Increase timeout values -->
    <property>
        <name>dfs.client.socket-timeout</name>
        <value>120000</value>
    </property>
</configuration>
EOF
echo "✅ HDFS configuration updated"
echo

# Step 5: Format the NameNode (option)
while true; do
    read -p "⚠️ Do you want to format the NameNode? This will ERASE ALL DATA in HDFS! (y/n): " yn
    case $yn in
        [Yy]* ) 
            echo "Formatting NameNode..."
            $HADOOP_HOME/bin/hdfs namenode -format
            echo "✅ NameNode formatted"
            break;;
        [Nn]* ) 
            echo "Skipping NameNode format"
            break;;
        * ) echo "Please answer yes or no.";;
    esac
done
echo

# Step 6: Restart HDFS services
echo "6️⃣ Starting HDFS services..."
$HADOOP_HOME/sbin/start-dfs.sh
echo "✅ HDFS services started"
echo

# Step 7: Verify services
echo "7️⃣ Verifying HDFS services..."
jps_output=$(jps)
echo "$jps_output"

if echo "$jps_output" | grep -q "NameNode" && echo "$jps_output" | grep -q "DataNode"; then
    echo "✅ NameNode and DataNode are running"
else
    echo "❌ Some HDFS services are not running"
    echo "Check logs for details: $HADOOP_HOME/logs/"
fi
echo

# Step 8: Check HDFS status
echo "8️⃣ Checking HDFS status..."
$HADOOP_HOME/bin/hdfs dfsadmin -report
echo

# Step 9: Create test file
echo "9️⃣ Testing HDFS write operation..."
echo "This is a test file" > /tmp/test_hdfs.txt
$HADOOP_HOME/bin/hdfs dfs -mkdir -p /user/hadoop/test 2>/dev/null
$HADOOP_HOME/bin/hdfs dfs -rm -skipTrash /user/hadoop/test/test.txt 2>/dev/null
if $HADOOP_HOME/bin/hdfs dfs -put /tmp/test_hdfs.txt /user/hadoop/test/test.txt; then
    echo "✅ Successfully wrote test file to HDFS"
    $HADOOP_HOME/bin/hdfs dfs -ls /user/hadoop/test/
    rm /tmp/test_hdfs.txt
else
    echo "❌ Failed to write test file to HDFS"
fi
echo

echo "===== HDFS Repair Complete ====="
echo "If you're still having issues, try the following:"
echo "1. Check logs in $HADOOP_HOME/logs/"
echo "2. Run 'hdfs fsck /' to check for file system errors"
echo "3. Consider formatting the namenode if problems persist"
echo