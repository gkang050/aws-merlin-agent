#!/bin/bash
set -e

echo "🚀 MERLIN EC2 Deployment Script"
echo "================================"
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS credentials not configured"
    exit 1
fi

REGION=${AWS_REGION:-us-east-1}
KEY_NAME="merlin-key"
INSTANCE_TYPE="t3.small"  # Free tier eligible: t2.micro, but t3.small is better
SECURITY_GROUP_NAME="merlin-sg"

echo "📋 Configuration:"
echo "   Region: $REGION"
echo "   Instance Type: $INSTANCE_TYPE"
echo "   Key Name: $KEY_NAME"
echo ""

# Step 1: Create key pair if it doesn't exist
echo "🔑 Step 1: Creating SSH key pair..."
if aws ec2 describe-key-pairs --key-names $KEY_NAME --region $REGION > /dev/null 2>&1; then
    echo "   ✓ Key pair already exists"
else
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --region $REGION \
        --query 'KeyMaterial' \
        --output text > ${KEY_NAME}.pem
    chmod 400 ${KEY_NAME}.pem
    echo "   ✓ Key pair created: ${KEY_NAME}.pem"
    echo "   ⚠️  SAVE THIS FILE! You'll need it to SSH into the instance"
fi
echo ""

# Step 2: Create security group
echo "🔒 Step 2: Creating security group..."
SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" \
    --region $REGION \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null)

if [ "$SG_ID" = "None" ] || [ -z "$SG_ID" ]; then
    VPC_ID=$(aws ec2 describe-vpcs \
        --filters "Name=isDefault,Values=true" \
        --region $REGION \
        --query 'Vpcs[0].VpcId' \
        --output text)
    
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP_NAME \
        --description "Security group for MERLIN Streamlit app" \
        --vpc-id $VPC_ID \
        --region $REGION \
        --query 'GroupId' \
        --output text)
    
    # Allow SSH
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    # Allow Streamlit (8501)
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 8501 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    echo "   ✓ Security group created: $SG_ID"
else
    echo "   ✓ Security group already exists: $SG_ID"
fi
echo ""

# Step 3: Get latest Amazon Linux 2023 AMI
echo "🖼️  Step 3: Getting latest AMI..."
AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=al2023-ami-2023.*-x86_64" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --region $REGION \
    --output text)
echo "   ✓ Using AMI: $AMI_ID"
echo ""

# Step 4: Create user data script
echo "📝 Step 4: Creating user data script..."
cat > user-data.sh << 'EOF'
#!/bin/bash
set -e

# Update system
yum update -y

# Install Python 3.11
yum install -y python3.11 python3.11-pip git

# Install poetry
pip3.11 install poetry

# Clone repository (you'll need to update this with your repo URL)
cd /home/ec2-user
git clone https://github.com/YOUR_USERNAME/aws-merlin-agent.git || echo "Using existing code"
cd aws-merlin-agent

# Install dependencies
poetry install

# Set environment variables
cat > /home/ec2-user/.merlin_env << 'ENVEOF'
export MERLIN_ENV=demo
export MERLIN_INFERENCE_MODE=local
export AWS_REGION=us-east-1
ENVEOF

# Create systemd service
cat > /etc/systemd/system/merlin.service << 'SERVICEEOF'
[Unit]
Description=MERLIN Streamlit App
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/aws-merlin-agent
EnvironmentFile=/home/ec2-user/.merlin_env
ExecStart=/usr/local/bin/poetry run streamlit run src/aws_merlin_agent/ui/chat_app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Start service
systemctl daemon-reload
systemctl enable merlin
systemctl start merlin

echo "MERLIN deployment complete!"
EOF

echo "   ✓ User data script created"
echo ""

# Step 5: Launch EC2 instance
echo "🚀 Step 5: Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SG_ID \
    --user-data file://user-data.sh \
    --region $REGION \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=MERLIN-Streamlit}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "   ✓ Instance launched: $INSTANCE_ID"
echo ""

# Step 6: Wait for instance to be running
echo "⏳ Step 6: Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION
echo "   ✓ Instance is running"
echo ""

# Step 7: Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "✅ Deployment Complete!"
echo "======================"
echo ""
echo "📊 Instance Details:"
echo "   Instance ID: $INSTANCE_ID"
echo "   Public IP: $PUBLIC_IP"
echo "   Region: $REGION"
echo ""
echo "🌐 Access MERLIN:"
echo "   URL: http://$PUBLIC_IP:8501"
echo "   (Wait 2-3 minutes for app to start)"
echo ""
echo "🔐 SSH Access:"
echo "   ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
echo ""
echo "📋 Useful Commands:"
echo "   Check status: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP 'sudo systemctl status merlin'"
echo "   View logs: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP 'sudo journalctl -u merlin -f'"
echo "   Restart: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP 'sudo systemctl restart merlin'"
echo ""
echo "💰 Cost: ~\$15-20/month (t3.small)"
echo ""
echo "🗑️  To delete:"
echo "   aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region $REGION"
echo ""
