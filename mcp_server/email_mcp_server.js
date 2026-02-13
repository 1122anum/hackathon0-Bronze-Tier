/**
 * MCP Email Server - Silver Tier
 * Handles email sending via SMTP with proper error handling
 *
 * This server provides an HTTP API for sending emails through MCP protocol
 */

const express = require('express');
const nodemailer = require('nodemailer');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.MCP_PORT || 3000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Logging setup
const logDir = path.join(__dirname, '..', 'logs');
if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
}

const logFile = path.join(logDir, 'mcp_server.log');

function log(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const logEntry = {
        timestamp,
        level,
        message,
        data
    };

    const logLine = JSON.stringify(logEntry) + '\n';
    fs.appendFileSync(logFile, logLine);

    console.log(`[${timestamp}] ${level}: ${message}`);
    if (data) {
        console.log(JSON.stringify(data, null, 2));
    }
}

// Load email configuration from environment
const emailConfig = {
    host: process.env.SMTP_HOST || 'smtp.gmail.com',
    port: parseInt(process.env.SMTP_PORT || '587'),
    secure: process.env.SMTP_SECURE === 'true',
    auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS
    }
};

// Create reusable transporter
let transporter = null;

function initializeTransporter() {
    try {
        transporter = nodemailer.createTransport(emailConfig);
        log('INFO', 'Email transporter initialized', {
            host: emailConfig.host,
            port: emailConfig.port,
            user: emailConfig.auth.user
        });
        return true;
    } catch (error) {
        log('ERROR', 'Failed to initialize email transporter', { error: error.message });
        return false;
    }
}

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'MCP Email Server',
        version: '1.0.0',
        timestamp: new Date().toISOString()
    });
});

// Send email endpoint
app.post('/send-email', async (req, res) => {
    const startTime = Date.now();

    try {
        log('INFO', 'Received email send request', {
            to: req.body.to,
            subject: req.body.subject
        });

        // Validate required fields
        const { to, subject, body } = req.body;

        if (!to || !subject || !body) {
            log('WARN', 'Missing required fields', req.body);
            return res.status(400).json({
                success: false,
                error: 'Missing required fields: to, subject, body'
            });
        }

        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(to)) {
            log('WARN', 'Invalid email format', { to });
            return res.status(400).json({
                success: false,
                error: 'Invalid email format'
            });
        }

        // Initialize transporter if not already done
        if (!transporter) {
            const initialized = initializeTransporter();
            if (!initialized) {
                return res.status(500).json({
                    success: false,
                    error: 'Email service not configured'
                });
            }
        }

        // Prepare email options
        const mailOptions = {
            from: emailConfig.auth.user,
            to: to,
            subject: subject,
            text: body,
            html: req.body.html || body.replace(/\n/g, '<br>')
        };

        // Add CC if provided
        if (req.body.cc) {
            mailOptions.cc = req.body.cc;
        }

        // Add BCC if provided
        if (req.body.bcc) {
            mailOptions.bcc = req.body.bcc;
        }

        // Send email
        const info = await transporter.sendMail(mailOptions);

        const duration = Date.now() - startTime;

        log('INFO', 'Email sent successfully', {
            messageId: info.messageId,
            to: to,
            subject: subject,
            duration: `${duration}ms`
        });

        res.json({
            success: true,
            message_id: info.messageId,
            timestamp: new Date().toISOString(),
            duration_ms: duration
        });

    } catch (error) {
        const duration = Date.now() - startTime;

        log('ERROR', 'Failed to send email', {
            error: error.message,
            stack: error.stack,
            duration: `${duration}ms`
        });

        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// Test email endpoint (for development)
app.post('/test-email', async (req, res) => {
    try {
        const testEmail = {
            to: req.body.to || emailConfig.auth.user,
            subject: 'MCP Email Server Test',
            body: 'This is a test email from the MCP Email Server.\n\nIf you received this, the server is working correctly!'
        };

        // Forward to send-email endpoint
        req.body = testEmail;
        return app._router.handle(req, res);

    } catch (error) {
        log('ERROR', 'Test email failed', { error: error.message });
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    log('ERROR', 'Unhandled error', {
        error: err.message,
        stack: err.stack,
        url: req.url,
        method: req.method
    });

    res.status(500).json({
        success: false,
        error: 'Internal server error',
        timestamp: new Date().toISOString()
    });
});

// Start server
app.listen(PORT, () => {
    log('INFO', `MCP Email Server started on port ${PORT}`);
    console.log('='.repeat(60));
    console.log('MCP Email Server - Silver Tier');
    console.log('='.repeat(60));
    console.log(`Server running on: http://localhost:${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/health`);
    console.log(`Send email: POST http://localhost:${PORT}/send-email`);
    console.log('='.repeat(60));

    // Initialize transporter on startup
    initializeTransporter();
});

// Graceful shutdown
process.on('SIGTERM', () => {
    log('INFO', 'SIGTERM received, shutting down gracefully');
    process.exit(0);
});

process.on('SIGINT', () => {
    log('INFO', 'SIGINT received, shutting down gracefully');
    process.exit(0);
});

module.exports = app;
