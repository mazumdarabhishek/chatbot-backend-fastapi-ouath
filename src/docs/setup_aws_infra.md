# AWS Infrastructure Setup Guide

This guide provides step-by-step instructions to manually set up AWS infrastructure using the AWS Console, including:
- EC2 instance (Free Tier eligible)
- API Gateway with HTTPS
- Connection between API Gateway and EC2

## Prerequisites

- AWS Account with Free Tier eligibility
- Basic understanding of AWS services
- Access to AWS Console

---

## Part 1: Create EC2 Instance (Free Tier)

### Step 1: Launch EC2 Instance

1. **Sign in to AWS Console**
   - Go to [AWS Console](https://console.aws.amazon.com/)
   - Sign in with your AWS account credentials

2. **Navigate to EC2 Service**
   - Search for "EC2" in the AWS services search bar
   - Click on "EC2" to open the EC2 Dashboard

3. **Launch Instance**
   - Click the orange "Launch instance" button
   - You'll be taken to the Launch Instance wizard

### Step 2: Configure Instance Details

4. **Name and Tags**
   - Enter a name for your instance (e.g., "chatbot-api-server")
   - Add any additional tags if needed

5. **Choose Amazon Machine Image (AMI)**
   - Select "Amazon Linux 2023 AMI" (Free tier eligible)
   - Ensure it shows "Free tier eligible" label
   - Click "Select"

6. **Choose Instance Type**
   - Select "t2.micro" (Free tier eligible)
   - This provides 1 vCPU and 1 GB RAM
   - Ensure "Free tier eligible" is displayed

7. **Key Pair (Login)**
   - If you have an existing key pair, select it
   - If not, click "Create new key pair":
     - Name: `chatbot-api-keypair`
     - Key pair type: RSA
     - Private key file format: .pem (for SSH)
     - Click "Create key pair" and download the .pem file
     - **Important**: Store this file securely - you'll need it to SSH into your instance

### Step 3: Configure Network Settings

8. **Network Settings**
   - Keep the default VPC and subnet
   - **Security Group**: Create a new security group or edit the default:
     - Name: `chatbot-api-sg`
     - Description: `Security group for chatbot API server`
     - **Add the following rules**:
       - SSH (Port 22): Source = My IP (for secure access)
       - HTTP (Port 80): Source = Anywhere (0.0.0.0/0)
       - HTTPS (Port 443): Source = Anywhere (0.0.0.0/0)
       - Custom TCP (Port 8000): Source = Anywhere (0.0.0.0/0) [for FastAPI]

### Step 4: Configure Storage

9. **Storage Configuration**
   - Keep default 8 GB gp3 storage (Free tier eligible)
   - This provides up to 30 GB free per month

### Step 5: Launch Instance

10. **Review and Launch**
    - Review all configurations
    - Click "Launch instance"
    - Wait for the instance to initialize (Status: Running)
    - Note down the **Public IPv4 address** and **Instance ID**

---

## Part 2: Set Up Your Application on EC2

### Step 6: Connect to EC2 Instance

11. **SSH into EC2 Instance**
    ```bash
    # Make the key file readable only by you
    chmod 400 /path/to/chatbot-api-keypair.pem
    
    # SSH into the instance
    ssh -i /path/to/chatbot-api-keypair.pem ec2-user@YOUR_EC2_PUBLIC_IP
    ```

### Step 7: Install Dependencies

12. **Update System and Install Python**
    ```bash
    # Update the system
    sudo yum update -y
    
    # Install Python 3 and pip
    sudo yum install python3 python3-pip git -y
    ```

13. **Set Up Your FastAPI Application**
    ```bash
    # Clone your repository or upload your code
    git clone YOUR_REPOSITORY_URL
    cd chatbot_fastapi/src
    
    # Install Python dependencies
    pip3 install -r requirements.txt
    
    # Install additional production dependencies
    pip3 install uvicorn gunicorn
    ```

### Step 8: Configure Application to Run on Boot

14. **Create Systemd Service File**
    ```bash
    sudo nano /etc/systemd/system/chatbot-api.service
    ```
    
    Add the following content:
    ```ini
    [Unit]
    Description=ChatBot FastAPI application
    After=network.target
    
    [Service]
    User=ec2-user
    Group=ec2-user
    WorkingDirectory=/home/ec2-user/chatbot_fastapi/src
    Environment="PATH=/home/ec2-user/.local/bin"
    ExecStart=/home/ec2-user/.local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
    Restart=always
    
    [Install]
    WantedBy=multi-user.target
    ```

15. **Start and Enable the Service**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl start chatbot-api
    sudo systemctl enable chatbot-api
    sudo systemctl status chatbot-api
    ```

---

## Part 3: Create API Gateway with HTTPS

### Step 9: Create API Gateway

16. **Navigate to API Gateway**
    - In AWS Console, search for "API Gateway"
    - Click on "API Gateway" service

17. **Create New API**
    - Click "Create API"
    - Choose "REST API" (not private)
    - Click "Build"

18. **Configure API Settings**
    - **API Name**: `chatbot-api-gateway`
    - **Description**: `API Gateway for ChatBot FastAPI application`
    - **Endpoint Type**: Regional
    - Click "Create API"

### Step 10: Create Resources and Methods

19. **Create Resource (Optional)**
    - Click "Actions" → "Create Resource"
    - **Resource Name**: `api`
    - **Resource Path**: `/api`
    - Check "Enable API Gateway CORS"
    - Click "Create Resource"

20. **Create Proxy Resource**
    - Select the root resource `/` (or `/api` if created)
    - Click "Actions" → "Create Resource"
    - **Resource Name**: `proxy`
    - **Resource Path**: `{proxy+}`
    - Check "Enable API Gateway CORS"
    - Click "Create Resource"

21. **Create ANY Method**
    - Select the `{proxy+}` resource
    - Click "Actions" → "Create Method"
    - Choose "ANY" from dropdown
    - Click the checkmark

### Step 11: Configure Integration

22. **Set Up HTTP Integration**
    - **Integration Type**: HTTP Proxy
    - **Use HTTP Proxy Integration**: Checked
    - **HTTP Method**: ANY
    - **Endpoint URL**: `http://YOUR_EC2_PUBLIC_IP:8000/{proxy}`
    - **Content Handling**: Passthrough
    - Click "Save"

### Step 12: Configure CORS (if needed)

23. **Enable CORS**
    - Select the `{proxy+}` resource
    - Click "Actions" → "Enable CORS"
    - **Access-Control-Allow-Origin**: `*` (or specific domains)
    - **Access-Control-Allow-Headers**: `Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token`
    - **Access-Control-Allow-Methods**: Select all methods needed
    - Click "Enable CORS and replace existing CORS headers"

### Step 13: Deploy API

24. **Create Deployment**
    - Click "Actions" → "Deploy API"
    - **Deployment stage**: `[New Stage]`
    - **Stage name**: `prod`
    - **Stage description**: `Production deployment`
    - **Deployment description**: `Initial deployment`
    - Click "Deploy"

25. **Note the Invoke URL**
    - After deployment, you'll see the **Invoke URL**
    - It will look like: `https://your-api-id.execute-api.region.amazonaws.com/prod`
    - This is your HTTPS endpoint!

---

## Part 4: Testing and Verification

### Step 17: Test Your Setup

26. **Test EC2 Instance Directly**
    ```bash
    curl http://YOUR_EC2_PUBLIC_IP:8000/
    ```

27. **Test API Gateway**
    ```bash
    curl https://your-api-id.execute-api.region.amazonaws.com/prod/
    ```

### Step 18: Monitor and Troubleshoot

28. **Check CloudWatch Logs**
    - Navigate to CloudWatch in AWS Console
    - Check API Gateway logs and EC2 instance logs
    - Monitor for any errors or issues

29. **Security Best Practices**
    - Regularly update your EC2 instance
    - Monitor security groups and access patterns
    - Use IAM roles and policies for fine-grained access control
    - Enable AWS CloudTrail for audit logging

---

## Important Notes

### Cost Optimization
- **Free Tier Limits**:
  - EC2: 750 hours per month of t2.micro
  - API Gateway: 1 million API calls per month
  - Data Transfer: 1 GB per month

### Security Considerations
- Keep your EC2 key pair secure
- Regularly update security groups
- Use HTTPS for all client communications
- Consider using AWS WAF for additional protection

### Maintenance
- Set up automated backups for your EC2 instance
- Monitor application logs
- Plan for scaling when you exceed free tier limits

---

## Troubleshooting Common Issues

### Issue 1: API Gateway 502 Bad Gateway
- **Cause**: EC2 instance is not running or application is not responding
- **Solution**: Check EC2 instance status and application logs

### Issue 2: Connection Timeout
- **Cause**: Security group is blocking traffic
- **Solution**: Verify security group rules allow traffic on required ports

### Issue 3: SSL Certificate Validation Fails
- **Cause**: DNS records not properly configured
- **Solution**: Double-check CNAME records in your domain's DNS

### Issue 4: CORS Errors
- **Cause**: API Gateway CORS not properly configured
- **Solution**: Re-configure CORS settings in API Gateway

---

## Next Steps

After completing this setup, you'll have:
✅ A running EC2 instance with your FastAPI application  
✅ HTTPS API Gateway endpoint  
✅ Secure connection between API Gateway and EC2  

Your API will be accessible via the default API Gateway HTTPS endpoint and ready for production use within AWS Free Tier limits.
